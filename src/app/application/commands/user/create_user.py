import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.authorization.authorize import (
    authorize,
)
from app.application.common.services.authorization.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.domain.services.user import UserService
from app.domain.value_objects.raw_password import RawPassword
from app.domain.value_objects.username import Username
from app.domain.value_objects.text import Email
from app.domain.value_objects.time import CreatedAt, UpdatedAt

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserRequest:
    username: str
    email: str
    password: str
    user_type: UserRole  # Changed from role to user_type for consistency


class CreateUserResponse(TypedDict):
    id: UUID


class CreateUserInteractor:

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        user_command_gateway: UserCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._user_command_gateway = user_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: CreateUserRequest) -> CreateUserResponse:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainFieldError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """
        log.info(
            "Create user: started. Username: '%s', Email: '%s'",
            request_data.username,
            request_data.email,
        )

        # Create value objects
        username = Username(request_data.username)
        email = Email(request_data.email)
        password = RawPassword(request_data.password)
        created_at = CreatedAt.now()
        updated_at = UpdatedAt.now()

        user = self._user_service.create_viewer(
            username=username,
            email=email,
            raw_password=password,
            user_type=request_data.user_type,
            created_at=created_at,
            updated_at=updated_at,
        )

        self._user_command_gateway.add(user)

        try:
            await self._flusher.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._transaction_manager.commit()

        log.info(
            "Create user: done. Username: '%s', Email: '%s', Type: %s",
            user.username.value,
            user.email.value,
            user.user_type.name,
        )
        return CreateUserResponse(id=user.id_.value)
