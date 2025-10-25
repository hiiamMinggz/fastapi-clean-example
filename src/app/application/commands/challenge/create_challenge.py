import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from app.application.common.ports.flusher import Flusher
from app.application.common.ports.streamer_profile_command_gateway import StreamerProfileCommandGateway
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.challenge_command_gateway import ChallengeCommandGateway

from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.ports.wallet_command_gateway import WalletCommandGateway
from app.application.common.services.current_user import CurrentUserService

from app.domain.enums.fee import Fee
from app.domain.enums.challenge_status import Status
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.base import DomainError
from app.domain.services.challenge import ChallengeService
from app.domain.services.wallet import WalletService
from app.domain.value_objects.text import Title, Description
from app.domain.value_objects.id import UserId
from app.domain.value_objects.token import ChallengeAmount
from app.domain.value_objects.time import CreatedAt, ExpiresAt

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateChallengeRequest:
    title: str
    description: str
    created_by: str
    assigned_to: str
    amount: str
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
        challenge_command_gateway: ChallengeCommandGateway,
        streamer_profile_gateway: StreamerProfileCommandGateway,
        wallet_command_gateway: WalletCommandGateway,
        user_command_gateway: UserCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._challenge_service = challenge_service
        self._wallet_service = wallet_service
        self._challenge_command_gateway = challenge_command_gateway
        self._streamer_profile_gateway = streamer_profile_gateway
        self._user_command_gateway = user_command_gateway
        self._wallet_command_gateway = wallet_command_gateway
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

        #check assigned_to is a valid streamer
        streamer_id = UserId(request_data.assigned_to)
        streamer = await self._user_command_gateway.read_by_id(streamer_id)
        if not streamer or streamer.user_type != UserRole.STREAMER:
            raise DomainError("Assigned to is not a valid streamer")
        
        streamer_profile = await self._streamer_profile_gateway.read_by_id(streamer_id)
        
        title = Title(request_data.title)
        description = Description(request_data.description)
        created_by = UserId(request_data.created_by)
        amount = ChallengeAmount(Decimal(request_data.amount))
        streamer_fixed_amount = streamer_profile.min_amount_challenge
        expires_at = ExpiresAt(request_data.expires_at)

        challenge = self._challenge_service.create_challenge(
            title=title,
            description=description,
            created_by=created_by,
            assigned_to=streamer_id,
            amount=amount,
            streamer_fixed_amount=streamer_fixed_amount,
            expires_at=expires_at,
        )
        #TODO: transfer amount from creator's wallet to HOLDER wallet
        current_user = await self._current_user_service.get_current_user()
        current_user_wallet = await self._wallet_command_gateway.read_by_id(current_user.id_)
        
        self._wallet_service.transfer(
            from_wallet=current_user_wallet,
            to_wallet=..., # HOLDER wallet
            amount=amount,
        )

        self._challenge_command_gateway.add(challenge)

        await self._flusher.flush()

        await self._transaction_manager.commit()

        log.info("Create challenge: done.")
        return CreateChallengeResponse(id=challenge.id_.value)
