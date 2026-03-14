import logging
from dataclasses import dataclass
from typing import TypedDict

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.transaction_command_gateway import TransactionCommandGateway
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.challenge_command_gateway import ChallengeCommandGateway
from app.application.common.ports.wallet_command_gateway import WalletCommandGateway
from app.application.common.services.authorization.authorize import (
    authorize,
)
from app.application.common.services.authorization.permissions import (
    CanChangeChallengeStatus,
    ChallengeManagementContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.base import DomainError
from app.domain.challenge.challenge import Challenge
from app.domain.challenge.exceptions import ChallengeNotFoundByIdError
from app.domain.challenge.challenge_status import ChallengeStatus
from app.domain.challenge.service import ChallengeService
from uuid import UUID
from datetime import datetime, timezone

from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.transaction.service import TransactionService
from app.domain.shared.entities.transaction.transaction import Transaction
from app.domain.shared.entities.transaction.value_objects import Allocation
from app.domain.shared.enums import ProductType
from app.domain.shared.value_objects.id import ProductId
from app.domain.wallet.service import WalletService
from app.domain.wallet.wallet import Wallet
from app.domain.base import DomainError
log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ToggleChallengeStatusRequest:
    challenge_id: UUID
    status: ChallengeStatus


class ToggleChallengeStatusResponse(TypedDict):
    message: str


class ToggleChallengeStatusInteractor:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        challenge_service: ChallengeService,
        wallet_service: WalletService,
        transaction_service: TransactionService,
        challenge_command_gateway: ChallengeCommandGateway,
        wallet_command_gateway: WalletCommandGateway,
        transaction_command_gateway: TransactionCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._challenge_service = challenge_service
        self._wallet_service = wallet_service
        self._transaction_service = transaction_service
        self._challenge_command_gateway = challenge_command_gateway
        self._wallet_command_gateway = wallet_command_gateway
        self._transaction_command_gateway = transaction_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: ToggleChallengeStatusRequest) -> None:
        """
        :raises AuthenticationError: If the current user is not authenticated
        :raises DataMapperError: If there's an error accessing the database
        :raises AuthorizationError: If the user is not authorized to update this challenge
        :raises DomainError: If the challenge is not found or cannot be updated
        :raises DomainFieldError: If the title or description is invalid
        """
        log.info(
            "Toggle challenge status: started. Challenge ID: %s",
            request_data.challenge_id,
        )

        current_user = await self._current_user_service.get_current_user()
        
        challenge_id = ProductId(request_data.challenge_id)
        new_status = request_data.status
        
        challenge: Challenge | None = await self._challenge_command_gateway.read_by_id(challenge_id)
        if challenge is None:
            raise ChallengeNotFoundByIdError()


        # Authorize: can only update challenges created by the current user
        authorize(
            CanChangeChallengeStatus(),
            context=ChallengeManagementContext(
                subject=current_user,
                challenge=challenge,
            ),
        )
        now = datetime.now(timezone.utc)

        handler_map = {
            ChallengeStatus.STREAMER_ACCEPTED: self._handle_streamer_accepted,
            ChallengeStatus.STREAMER_REJECTED: self._handle_streamer_rejected,
            ChallengeStatus.VIEWER_REJECTED: self._handle_viewer_rejected,
            ChallengeStatus.STREAMER_COMPLETED: self._handle_streamer_completed,
            ChallengeStatus.VIEWER_CONFIRMED: self._handle_viewer_confirmed,
        }
        handler = handler_map.get(new_status)
        if handler is None:
            raise DomainError(f"Unsupported challenge status: {new_status}")

        transaction = await handler(
            challenge=challenge,
            changed_by=current_user.id_,
            now=now,
        )

        if transaction is not None:
            self._transaction_command_gateway.add(transaction)
        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "Toggle challenge status: done. Challenge ID: %s",
            challenge_id,
        )
        return ToggleChallengeStatusResponse(message=f"Challenge {challenge_id} status {challenge.status} changed to {new_status}")

    async def _get_wallet_or_error(self, user_id, *, label: str) -> Wallet:
        wallet = await self._wallet_command_gateway.read_by_user_id(
            user_id,
            for_update=True,
        )
        if wallet is None:
            raise DomainError(f"{label} wallet not found")
        return wallet

    async def _handle_streamer_accepted(
        self,
        *,
        challenge: Challenge,
        changed_by,
        now: datetime,
    ) -> Transaction | None:
        self._challenge_service.streamer_accept_challenge(
            challenge=challenge,
            changed_by=changed_by,
        )
        # TODO: Add notification to viewer
        return None

    async def _handle_streamer_rejected(
        self,
        *,
        challenge: Challenge,
        changed_by,
        now: datetime,
    ) -> Transaction:
        self._challenge_service.streamer_reject_challenge(
            challenge=challenge,
            changed_by=changed_by,
        )
        viewer_wallet = await self._get_wallet_or_error(
            challenge.created_by,
            label="Viewer",
        )
        self._wallet_service.credit(
            wallet=viewer_wallet,
            amount=challenge.amount,
        )
        allocations = (
            Allocation(
                payee_type=AccountType.USER_WALLET,
                payee_id=viewer_wallet.id_,
                amount=challenge.amount,
            ),
        )
        return self._transaction_service.create_escrow_release_transaction(
            allocations=allocations,
            amount=challenge.amount,
            reference_id=challenge.id_,
            reference_type=ProductType.CHALLENGE,
        )

    async def _handle_viewer_rejected(
        self,
        *,
        challenge: Challenge,
        changed_by,
        now: datetime,
    ) -> Transaction:
        self._challenge_service.viewer_reject_challenge(
            challenge=challenge,
            changed_by=changed_by,
        )
        # TODO: Add notification to streamer
        current_duration = now - challenge.created_at.value
        if current_duration <= challenge.duration * 0.3:
            viewer_wallet = await self._get_wallet_or_error(
                challenge.created_by,
                label="Viewer",
            )
            self._wallet_service.credit(
                wallet=viewer_wallet,
                amount=challenge.amount,
            )
            allocations = (
                Allocation(
                    payee_type=AccountType.USER_WALLET,
                    payee_id=viewer_wallet.id_,
                    amount=challenge.amount,
                ),
            )
            return self._transaction_service.create_escrow_release_transaction(
                allocations=allocations,
                amount=challenge.amount,
                reference_id=challenge.id_,
                reference_type=ProductType.CHALLENGE,
            )

        if current_duration >= challenge.duration:
            dareus_earn = challenge.amount * 0.1
            viewer_get_back = challenge.amount - dareus_earn

            viewer_wallet = await self._get_wallet_or_error(
                challenge.created_by,
                label="Viewer",
            )
            self._wallet_service.credit(
                wallet=viewer_wallet,
                amount=viewer_get_back,
            )
            allocations = (
                Allocation(
                    payee_type=AccountType.REVENUE,
                    payee_id=None,
                    amount=dareus_earn,
                ),
                Allocation(
                    payee_type=AccountType.USER_WALLET,
                    payee_id=viewer_wallet.id_,
                    amount=viewer_get_back,
                ),
            )
            return self._transaction_service.create_escrow_release_transaction(
                allocations=allocations,
                amount=challenge.amount,
                reference_id=challenge.id_,
                reference_type=ProductType.CHALLENGE,
            )

        dareus_earn = challenge.amount * 0.1
        streamer_earn = challenge.amount * 0.2
        viewer_get_back = challenge.amount - dareus_earn - streamer_earn

        viewer_wallet = await self._get_wallet_or_error(
            challenge.created_by,
            label="Viewer",
        )
        self._wallet_service.credit(
            wallet=viewer_wallet,
            amount=viewer_get_back,
        )

        streamer_wallet = await self._get_wallet_or_error(
            challenge.assigned_to,
            label="Streamer",
        )
        self._wallet_service.credit(
            wallet=streamer_wallet,
            amount=streamer_earn,
        )
        allocations = (
            Allocation(
                payee_type=AccountType.REVENUE,
                payee_id=None,
                amount=dareus_earn,
            ),
            Allocation(
                payee_type=AccountType.USER_WALLET,
                payee_id=streamer_wallet.id_,
                amount=streamer_earn,
            ),
            Allocation(
                payee_type=AccountType.USER_WALLET,
                payee_id=viewer_wallet.id_,
                amount=viewer_get_back,
            ),
        )
        return self._transaction_service.create_escrow_release_transaction(
            allocations=allocations,
            amount=challenge.amount,
            reference_id=challenge.id_,
            reference_type=ProductType.CHALLENGE,
        )

    async def _handle_streamer_completed(
        self,
        *,
        challenge: Challenge,
        changed_by,
        now: datetime,
    ) -> Transaction | None:
        self._challenge_service.streamer_complete_challenge(
            challenge=challenge,
            changed_by=changed_by,
        )
        # TODO: Add notification to viewer to confirm challenge
        return None

    async def _handle_viewer_confirmed(
        self,
        *,
        challenge: Challenge,
        changed_by,
        now: datetime,
    ) -> Transaction:
        self._challenge_service.viewer_confirm_challenge(
            challenge=challenge,
            changed_by=changed_by,
        )
        dareus_earn = challenge.amount * 0.1
        streamer_earn = challenge.amount - dareus_earn

        streamer_wallet = await self._get_wallet_or_error(
            challenge.assigned_to,
            label="Streamer",
        )
        self._wallet_service.credit(
            wallet=streamer_wallet,
            amount=streamer_earn,
        )
        allocations = (
            Allocation(
                payee_type=AccountType.REVENUE,
                payee_id=None,
                amount=dareus_earn,
            ),
            Allocation(
                payee_type=AccountType.USER_WALLET,
                payee_id=streamer_wallet.id_,
                amount=streamer_earn,
            ),
        )
        return self._transaction_service.create_escrow_release_transaction(
            allocations=allocations,
            amount=challenge.amount,
            reference_id=challenge.id_,
            reference_type=ProductType.CHALLENGE,
        )
