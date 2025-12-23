import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.transaction_manager import TransactionManager
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.ports.wallet_command_gateway import WalletCommandGateway
from app.application.common.services.current_user import CurrentUserService
from app.domain.user.user_role import UserRole
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.domain.services.user import UserService
from app.domain.services.wallet import WalletService
from app.domain.value_objects.raw_password import RawPassword
from app.domain.value_objects.text import Email
from app.domain.user.value_objects import Username
from app.infrastructure.auth.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.infrastructure.auth.handlers.constants import (
    AUTH_ALREADY_AUTHENTICATED,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ViewerSignUpRequest:
    username: str
    password: str
    email: str


class ViewerSignUpResponse(TypedDict):
    id: UUID


class ViewerSignUpHandler:
    """
    - Open to everyone.
    - Registers a new user with validation and uniqueness checks.
    - Passwords are peppered, salted, and stored as hashes.
    - A logged-in user cannot sign up until the session expires or is terminated.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        user_command_gateway: UserCommandGateway,
        wallet_service: WalletService,
        wallet_command_gateway: WalletCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._user_command_gateway = user_command_gateway
        self._wallet_service = wallet_service
        self._wallet_command_gateway = wallet_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: ViewerSignUpRequest) -> ViewerSignUpResponse:
        """
        :raises AlreadyAuthenticatedError:
        :raises AuthorizationError:
        :raises DataMapperError:
        :raises DomainFieldError:
        :raises RoleAssignmentNotPermittedError:
        :raises UsernameAlreadyExistsError:
        """
        log.info("Sign up: started. Username: '%s'.", request_data.username)

        try:
            await self._current_user_service.get_current_user()
            raise AlreadyAuthenticatedError(AUTH_ALREADY_AUTHENTICATED)
        except AuthenticationError:
            pass

        username = Username(request_data.username)
        password = RawPassword(request_data.password)
        email = Email(request_data.email)
        
        viewer = self._user_service.create_viewer(
            username=username,
            raw_password=password,
            email=email,
        )
        viewer_wallet = self._wallet_service.create_wallet(
            user_id=viewer.id_,
        )

        self._user_command_gateway.add(viewer)
        self._wallet_command_gateway.add(viewer_wallet)

        try:
            await self._flusher.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._transaction_manager.commit()

        log.info("Viewer sign up: done. Username: '%s'.", viewer.username.value)
        return ViewerSignUpResponse(id=viewer.id_.value)
