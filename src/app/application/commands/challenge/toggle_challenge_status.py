import logging
from dataclasses import dataclass

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
from app.domain.challenge.challenge import Challenge
from app.domain.challenge.exceptions import ChallengeNotFoundByIdError
from app.domain.challenge.value_objects import ChallengeId
from app.domain.challenge.challenge_status import ChallengeStatus
from app.domain.challenge.service import ChallengeService
from uuid import UUID
from datetime import datetime, timezone

from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.ledger.service import LedgerService
from app.domain.shared.entities.transaction.service import TransactionService
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.value_objects.time import AcceptedAt, CreatedAt, UpdatedAt
from app.domain.shared.value_objects.token import Token
from app.domain.wallet.service import WalletService
log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ToggleChallengeStatusRequest:
    challenge_id: UUID
    status: ChallengeStatus


class ToggleChallengeStatusInteractor:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        challenge_service: ChallengeService,
        wallet_service: WalletService,
        transaction_service: TransactionService,
        ledger_service : LedgerService,
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
        self._ledger_service = ledger_service
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
        
        challenge_id = ChallengeId(request_data.challenge_id)
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
        if new_status == ChallengeStatus.STREAMER_ACCEPTED:
            self._challenge_service.streamer_accept_challenge(
                challenge=challenge,
            )
            #TODO: Add notification to viewer
        elif new_status == ChallengeStatus.STREAMER_REJECTED:
            # update challenge status
            self._challenge_service.streamer_reject_challenge(
                challenge=challenge,
            )
            # refund full amount to viewer
            viewer_wallet = await self._wallet_command_gateway.read_by_user_id(
                challenge.assigned_to,
                for_update=True,
            )
            self._wallet_service.credit(
                wallet=viewer_wallet,
                amount=challenge.amount
            )
            # init double entry ledger
            escrow_debit_entry = self._ledger_service.create_escrow_debit_entry(
                debit=challenge.amount,
                created_at=CreatedAt(now),
            )
            user_wallet_credit_entry = self._ledger_service.create_user_wallet_credit_entry(
                account_id=viewer_wallet.id_,
                credit=challenge.amount,
                created_at=CreatedAt(now),
            )
            
            transaction = self._transaction_service.create_transaction(
                transaction_type=TransactionType.ESCROW_RELEASE,
                amount=challenge.amount,
                reference_id=challenge.id_,
                ledger_entries=[escrow_debit_entry, user_wallet_credit_entry],
                metadata={"reason": "Challenge Rejected by Streamer"},
            )
            
        elif new_status == ChallengeStatus.VIEWER_REJECTED:
            self._challenge_service.viewer_reject_challenge(
                challenge=challenge,
            )
            #TODO: Add notification to streamer
            #release escrow based on time policy
            current_duration = now - challenge.created_at.value
            if current_duration <= challenge.duration * 0.3:
                # refund full amount to viewer
                viewer_wallet = await self._wallet_command_gateway.read_by_user_id(
                    challenge.assigned_to,
                    for_update=True,
                )
                self._wallet_service.credit(
                    wallet=viewer_wallet,
                    amount=challenge.amount
                )
                # init double entry ledger
                escrow_debit_entry = self._ledger_service.create_escrow_debit_entry(
                    debit=challenge.amount,
                    created_at=CreatedAt(now),
                )
                user_wallet_credit_entry = self._ledger_service.create_user_wallet_credit_entry(
                    account_id=viewer_wallet.id_,
                    credit=challenge.amount,
                    created_at=CreatedAt(now),
                )
                
                transaction = self._transaction_service.create_transaction(
                    transaction_type=TransactionType.ESCROW_RELEASE,
                    amount=challenge.amount,
                    reference_id=challenge.id_,
                    ledger_entries=[escrow_debit_entry, user_wallet_credit_entry],
                    metadata={"reason": "Challenge Rejected by Streamer"},
                )
                
            elif current_duration >= challenge.duration:
                # Refund 90% to viewer and 10% to EARNER wallet
                dareus_earn = challenge.amount * 0.1
                viewer_get_back = challenge.amount - dareus_earn
                
                viewer_wallet = await self._wallet_command_gateway.read_by_user_id(
                    challenge.assigned_to,
                    for_update=True,
                )
                self._wallet_service.credit(
                    wallet=viewer_wallet,
                    amount=viewer_get_back
                )
                #debit ESCROW
                escrow_debit_entry = self._ledger_service.create_escrow_debit_entry(
                    debit=challenge.amount,
                    created_at=CreatedAt(now),
                )
                # credit earner
                commission_credit_entry = self._ledger_service.create_commission_credit_entry(
                    credit=dareus_earn,
                    created_at=CreatedAt(now),
                )
                #credit user_wallet
                user_wallet_credit_entry = self._ledger_service.create_user_wallet_credit_entry(
                    account_id=viewer_wallet.id_,
                    credit=viewer_get_back,
                    created_at=CreatedAt(now),
                )
                #write transaction
                transaction = self._transaction_service.create_transaction(
                    transaction_type=TransactionType.ESCROW_RELEASE,
                    amount=challenge.amount,
                    reference_id=challenge.id_,
                    ledger_entries=[escrow_debit_entry, commission_credit_entry, user_wallet_credit_entry],
                    metadata={"reason": "Challenge Rejected by Streamer"},
                )
            else:
                # Refund 70% to viewer and 10% to EARNER wallet and 20% to streamer
                dareus_earn = challenge.amount * 0.1
                streamer_earn = challenge.amount * 0.2
                viewer_get_back = challenge.amount - dareus_earn - streamer_earn
                
                viewer_wallet = await self._wallet_command_gateway.read_by_user_id(
                    challenge.created_by,
                    for_update=True,
                )
                self._wallet_service.credit(
                    wallet=viewer_wallet,
                    amount=viewer_get_back
                )

                streamer_wallet = await self._wallet_command_gateway.read_by_user_id(
                    challenge.assigned_to,
                    for_update=True,
                )
                self._wallet_service.credit(
                    wallet=streamer_wallet,
                    amount=streamer_earn
                )
                #debit ESCROW
                escrow_debit_entry = self._ledger_service.create_escrow_debit_entry(
                    debit=challenge.amount,
                    created_at=CreatedAt(now),
                )
                # credit earner
                commission_credit_entry = self._ledger_service.create_commission_credit_entry(
                    credit=dareus_earn,
                    created_at=CreatedAt(now),
                )
                #credit user_wallet
                viewer_wallet_credit_entry = self._ledger_service.create_user_wallet_credit_entry(
                    account_id=viewer_wallet.id_,
                    credit=viewer_get_back,
                    created_at=CreatedAt(now),
                )
                streamer_wallet_credit_entry = self._ledger_service.create_user_wallet_credit_entry(
                    account_id=streamer_wallet.id_,
                    credit=streamer_earn,
                    created_at=CreatedAt(now),
                )
                #write transaction
                transaction = self._transaction_service.create_transaction(
                    transaction_type=TransactionType.ESCROW_RELEASE,
                    amount=challenge.amount,
                    reference_id=challenge.id_,
                    ledger_entries=[escrow_debit_entry, commission_credit_entry, viewer_wallet_credit_entry, streamer_wallet_credit_entry],
                    metadata={"reason": "Challenge Rejected by Streamer"},
                )
            
            
        elif new_status == ChallengeStatus.STREAMER_COMPLETED:
            self._challenge_service.streamer_complete_challenge(
                challenge=challenge,
            )
            #TODO: Add notification to viewer to confirm challenge
            
        elif new_status == ChallengeStatus.VIEWER_CONFIRMED:
            self._challenge_service.viewer_confirm_challenge(
                challenge=challenge,
            )
            dareus_earn = challenge.amount * 0.1
            streamer_earn = challenge.amount - dareus_earn

            streamer_wallet = await self._wallet_command_gateway.read_by_user_id(
                challenge.assigned_to,
                for_update=True,
            )
            self._wallet_service.credit(
                wallet=streamer_wallet,
                amount=streamer_earn
            )
            
            escrow_debit_entry = self._ledger_service.create_escrow_debit_entry(
                debit=challenge.amount,
                created_at=CreatedAt(now),
            )
            commission_credit_entry = self._ledger_service.create_commission_credit_entry(
                credit=dareus_earn,
                created_at=CreatedAt(now),
            )
            streamer_wallet_credit_entry = self._ledger_service.create_user_wallet_credit_entry(
                account_id=streamer_wallet.id_,
                credit=streamer_earn,
                created_at=CreatedAt(now),
            )

            transaction = self._transaction_service.create_transaction(
                transaction_type=TransactionType.ESCROW_RELEASE,
                amount=challenge.amount,
                reference_id=challenge.id_,
                ledger_entries=[escrow_debit_entry, commission_credit_entry, streamer_wallet_credit_entry],
                metadata={"reason": "Challenge Completed by Viewer"},
            )
        
        self._transaction_command_gateway.add(transaction)
        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "Toggle challenge status: done. Challenge ID: %s",
            challenge_id,
        )
