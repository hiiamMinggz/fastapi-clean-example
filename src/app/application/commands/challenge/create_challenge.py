import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from app.application.common.ports.flusher import Flusher
from app.application.common.ports.streamer_profile_command_gateway import StreamerProfileCommandGateway
from app.application.common.ports.transaction_command_gateway import TransactionCommandGateway
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.challenge_command_gateway import ChallengeCommandGateway

from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.ports.wallet_command_gateway import WalletCommandGateway
from app.application.common.services.current_user import CurrentUserService

from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.user.user_role import UserRole
from app.domain.base import DomainError
from app.domain.challenge.service import ChallengeService
from app.domain.wallet.service import WalletService
from app.domain.shared.entities.transaction.service import TransactionService
from app.domain.shared.entities.ledger.service import LedgerService
from app.domain.challenge.value_objects import (
    Title,
    Description,
    ChallengeAmount,
)
from app.domain.user.value_objects import UserId
from app.domain.shared.value_objects.time import CreatedAt, ExpiresAt
from app.domain.shared.value_objects.token import Token

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateChallengeRequest:
    title: str
    description: str
    assigned_to: UUID
    amount: Decimal
    expires_at: datetime


class CreateChallengeResponse(TypedDict):
    id: UUID


class CreateChallengeInteractor:
    """
    - Creates a new challenge with the specified parameters
    - Validates all challenge parameters through domain entities
    - Persists the new challenge in the database
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        challenge_service: ChallengeService,
        wallet_service: WalletService,
        transaction_service: TransactionService,
        ledger_service : LedgerService,
        user_command_gateway: UserCommandGateway,
        streamer_profile_gateway: StreamerProfileCommandGateway,
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
        self._user_command_gateway = user_command_gateway
        self._streamer_profile_gateway = streamer_profile_gateway
        self._challenge_command_gateway = challenge_command_gateway
        self._wallet_command_gateway = wallet_command_gateway
        self._transaction_command_gateway = transaction_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: CreateChallengeRequest) -> CreateChallengeResponse:
        """
        :raises AuthenticationError: If the current user is not authenticated
        :raises DataMapperError: If there's an error persisting the challenge
        :raises AuthorizationError: If the user is not authorized to create challenges
        :raises DomainFieldError: If any of the challenge fields are invalid
        :raises DomainError: If challenge business rules are violated
        """
        log.info("Create challenge: started.")
        #get current user
        current_user = await self._current_user_service.get_current_user()

        #check assigned_to is a valid streamer
        streamer_id = UserId(request_data.assigned_to)
        streamer = await self._user_command_gateway.read_by_id(streamer_id)
        streamer_profile = await self._streamer_profile_gateway.read_by_id(streamer_id)
        
        if streamer is None or streamer_profile is None or streamer.role != UserRole.STREAMER:
            raise DomainError("Assigned to is not a valid streamer")
        
        challenge_amount = ChallengeAmount(request_data.amount)
        
        #create challenge
        challenge = self._challenge_service.create_challenge(
            title=Title(request_data.title),
            description=Description(request_data.description),
            created_by=current_user.id_,
            assigned_to=streamer_id,
            amount=challenge_amount,
            streamer_fixed_amount=streamer_profile.min_amount_challenge,
            expires_at=ExpiresAt(request_data.expires_at),
        )
        #debit wallet
        current_user_wallet = await self._wallet_command_gateway.read_by_user_id(
            current_user.id_,
            for_update=True,
        )
        if current_user_wallet is None:
            raise DomainError("Current user wallet not found")
        
        self._wallet_service.debit(
            wallet=current_user_wallet,
            amount = challenge_amount,
        )
        # init double entry ledger
        user_wallet_debit_entry = self._ledger_service.create_user_wallet_debit_entry(
            account_id=current_user_wallet.id_,
            debit=challenge_amount,
        )
        escrow_credit_entry = self._ledger_service.create_escrow_credit_entry(
            credit=challenge_amount,
        )
        # write transaction
        transaction = self._transaction_service.create_transaction(
            transaction_type=TransactionType.ESCROW_LOCK,
            amount=challenge_amount,
            reference_id=challenge.id_,
            ledger_entries=[user_wallet_debit_entry, escrow_credit_entry],
            metadata={"reason": "Challenge Created"},
        )
        self._challenge_command_gateway.add(challenge)
        self._transaction_command_gateway.add(transaction)
        
        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info("Create challenge: done.")
        return CreateChallengeResponse(id=challenge.id_.value)
