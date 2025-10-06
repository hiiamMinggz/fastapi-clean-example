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
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.streamer_profile import StreamerProfile
from app.domain.entities.user import User
from app.domain.enums.fee import Fee
from app.domain.enums.challenge_status import Status
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.base import DomainError
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.domain.services.challenge import ChallengeService
from app.domain.value_objects.text import Title, Description
from app.domain.value_objects.id import UserId
from app.domain.value_objects.token import ChallengeAmount, StreamerChallengeFixedAmount
from app.domain.value_objects.time import CreatedAt, ExpiresAt, AcceptedAt

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
        challenge_command_gateway: ChallengeCommandGateway,
        streamer_profile_gateway: StreamerProfileCommandGateway,
        user_command_gateway: UserCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._challenge_service = challenge_service
        self._challenge_command_gateway = challenge_command_gateway
        self._streamer_profile_gateway = streamer_profile_gateway
        self._user_command_gateway = user_command_gateway
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

        now = datetime.now(timezone.utc)

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
        fee = Fee.CHALLENGE_FEE
        
        streamer_fixed_amount = streamer_profile.min_amount_challenge
        status = Status.PENDING  # Always PENDING when created
        created_at = CreatedAt(now)
        expires_at = ExpiresAt(request_data.expires_at)

        challenge = self._challenge_service.create_challenge(
            title=title,
            description=description,
            created_by=created_by,
            assigned_to=streamer_id,
            amount=amount,
            fee=fee,
            streamer_fixed_amount=streamer_fixed_amount,
            status=status,
            created_at=created_at,
            expires_at=expires_at,
            accepted_at=None,
        )

        self._challenge_command_gateway.add(challenge)

        await self._flusher.flush()

        await self._transaction_manager.commit()

        log.info("Create challenge: done.")
        return CreateChallengeResponse(id=challenge.id_.value)
