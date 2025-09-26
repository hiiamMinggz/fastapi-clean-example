import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.application.common.ports.flusher import Flusher
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.challenge_command_gateway import UserCommandGateway
from app.application.common.ports.challenge_command_gateway import ChallengeCommandGateway

from app.application.common.services.current_user import CurrentUserService
from app.domain.enums.fee import Fee
from app.domain.enums.challenge_status import Status
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.domain.services.challenge import ChallengeService
from app.domain.value_objects.text import Title, Description
from app.domain.value_objects.id import ViewerId, StreamerId
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
    fee: Fee
    streamer_fixed_amount: str
    status: Status
    created_at: datetime
    expires_at: datetime
    accepted_at: datetime


class CreateChallengeResponse(TypedDict):
    id: UUID



class CreateUserInteractor:
    """
    - Open to admins.
    - Creates a new user, including admins, if the username is unique.
    - Only super admins can create new admins.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        challenge_service: ChallengeService,
        challenge_command_gateway: ChallengeCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._challenge_service = challenge_service
        self._challenge_command_gateway = challenge_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: CreateChallengeRequest) -> CreateChallengeResponse:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainFieldError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """
        log.info("Create challenge: started.")

        # current_user = await self._current_challenge_service.get_current_user()

        # authorize(
        #     CanManageRole(),
        #     context=RoleManagementContext(
        #         subject=current_user,
        #         target_role=request_data.role,
        #     ),
        # )

        title = Title(request_data.title)
        description = Description(request_data.description)
        created_by = ViewerId(request_data.created_by)
        assigned_to = StreamerId(request_data.assigned_to)
        amount = ChallengeAmount(Decimal(request_data.amount))
        fee = Fee(request_data.fee)
        streamer_fixed_amount = StreamerChallengeFixedAmount(Decimal(request_data.streamer_fixed_amount))
        status = Status(request_data.status)
        created_at = CreatedAt(request_data.created_at)
        expires_at = ExpiresAt(request_data.expires_at)
        accepted_at = AcceptedAt(request_data.accepted_at)

        challenge = self._challenge_service.create_challenge(
            title=title,
            description=description,
            created_by=created_by,
            assigned_to=assigned_to,
            amount=amount,
            fee=fee,
            streamer_fixed_amount=streamer_fixed_amount,
            status=status,
            created_at=created_at,
            expires_at=expires_at,
            accepted_at=accepted_at,
        )

        self._challenge_command_gateway.add(challenge)

        try:
            await self._flusher.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._transaction_manager.commit()

        log.info("Create challenge: done.")
        return CreateChallengeResponse(id=challenge.id_.value)
