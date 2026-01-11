import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import TypedDict
from uuid import UUID

from app.application.common.ports.streamer_command_gateway import StreamerCommandGateway
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.authorization.authorize import (
    authorize,
)
from app.application.common.services.authorization.composite import AnyOf
from app.application.common.services.authorization.permissions import (
    CanManageSelf,
    CanManageSubordinate,
    UserManagementContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.user.exceptions import UserNotFoundByUserIdError
from app.domain.user.service import UserService
from app.domain.user.streamer import Streamer
from app.domain.user.value_objects import (
    StreamerChallengeFixedAmount,
    UserId,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplyAsStreamerRequest:
    user_id: UUID
    min_amount_challenge: Decimal
    disable_challenges: bool


class ApplyAsStreamerResponse(TypedDict):
    id: UUID


class ApplyAsStreamerInteractor:
    """
    - Open to authenticated users.
    - Lets a viewer apply to become a streamer with their own challenge settings.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_command_gateway: UserCommandGateway,
        streamer_command_gateway: StreamerCommandGateway,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._user_command_gateway = user_command_gateway
        self._streamer_command_gateway = streamer_command_gateway
        self._user_service = user_service
        self._transaction_manager = transaction_manager

    async def execute(
        self,
        request_data: ApplyAsStreamerRequest,
    ) -> ApplyAsStreamerResponse:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainFieldError:
        :raises RoleAssignmentNotPermittedError:
        :raises UserNotFoundByUserIdError:
        """
        log.info(
            "Apply as streamer: started. UserId: '%s'.",
            request_data.user_id,
        )

        current_user = await self._current_user_service.get_current_user()

        user_id = UserId(request_data.user_id)
        user = await self._user_command_gateway.read_by_id(
            user_id,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundByUserIdError(user_id)

        authorize(
            AnyOf(
                CanManageSelf(),
                CanManageSubordinate(),
            ),
            context=UserManagementContext(
                subject=current_user,
                target=user,
            ),
        )

        streamer: Streamer = self._user_service.apply_as_streamer(
            user,
            min_amount_challenge=StreamerChallengeFixedAmount(
                request_data.min_amount_challenge,
            ),
            disable_challenges=request_data.disable_challenges,
        )
        self._user_service.toggle_user_role(user, is_streamer=True)

        self._streamer_command_gateway.add(streamer)
        
        await self._transaction_manager.commit()

        log.info(
            "Apply as streamer: done. UserId: '%s', StreamerId: '%s'.",
            user.id_.value,
            streamer.id_.value,
        )
        return ApplyAsStreamerResponse(id=streamer.id_.value)
