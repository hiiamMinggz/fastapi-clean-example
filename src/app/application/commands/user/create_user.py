import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.ports.wallet_command_gateway import WalletCommandGateway
from app.application.common.services.current_user import CurrentUserService
from app.domain.user.user_role import UserRole

from app.domain.user.value_objects import (
    Username,
    Email,
    RawPassword,
)
from app.domain.user.exceptions import UsernameAlreadyExistsError
from app.domain.user.service import UserService
from app.domain.wallet.service import WalletService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserRequest:
    username: str
    email: str
    password: str
    user_type: UserRole


class CreateUserResponse(TypedDict):
    id: UUID


class CreateUserInteractor:

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        wallet_service: WalletService,
        user_command_gateway: UserCommandGateway,
        wallet_command_gateway: WalletCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._wallet_service = wallet_service
        self._user_command_gateway = user_command_gateway
        self._wallet_command_gateway = wallet_command_gateway
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

        username = Username(request_data.username)
        email = Email(request_data.email)
        password = RawPassword(request_data.password)

        user = self._user_service.create_user(
            username=username,
            email=email,
            raw_password=password,
            user_type=request_data.user_type,
        )
        wallet = self._wallet_service.create_wallet(
            user_id=user.id_,
        )
        self._user_command_gateway.add(user)
        self._wallet_command_gateway.add(wallet)
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
