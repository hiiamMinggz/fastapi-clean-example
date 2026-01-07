import logging
from dataclasses import dataclass
from uuid import UUID

from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.authorization.authorize import (
    authorize,
)
from app.application.common.services.authorization.permissions import (
    CanManageRole,
    CanManageSubordinate,
    RoleManagementContext,
    UserManagementContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.user.user import User
from app.domain.user.user_role import UserRole
from app.domain.user.exceptions import UserNotFoundByUserIdError, UserNotFoundByUsernameError
from app.domain.user.service import UserService
from app.domain.user.value_objects import UserId, Username

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ActivateUserRequest:
    user_id: UUID


class ActivateUserInteractor:
    """
    - Open to admins.
    - Restores a previously soft-deleted user.
    - Only super admins can activate other admins.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_command_gateway: UserCommandGateway,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._user_command_gateway = user_command_gateway
        self._user_service = user_service
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: ActivateUserRequest) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainFieldError:
        :raises UserNotFoundByUsernameError:
        :raises ActivationChangeNotPermittedError:
        """
        log.info(
            "Activate user: started. UserId: '%s'.",
            request_data.user_id,
        )

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.VIEWER,
            ),
        )

        user_id = UserId(request_data.user_id)
        user: User | None = await self._user_command_gateway.read_by_id(
            user_id,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundByUserIdError(user_id)

        authorize(
            CanManageSubordinate(),
            context=UserManagementContext(
                subject=current_user,
                target=user,
            ),
        )

        self._user_service.toggle_user_activation(user, is_active=True)
        await self._transaction_manager.commit()

        log.info(
            "Activate user: done. UserId: '%s', Username: '%s'.",
            user.id_.value,
            user.username.value,
        )
