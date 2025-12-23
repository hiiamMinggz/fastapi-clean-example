from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from app.application.commands.user.create_user import (
    CreateUserInteractor,
    CreateUserRequest,
    CreateUserResponse,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.user.user_role import UserRole
from app.domain.exceptions.base import DomainFieldError
from app.domain.exceptions.user import (
    RoleAssignmentNotPermittedError,
    UsernameAlreadyExistsError,
)
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.domain.user.value_objects import Username
from app.domain.value_objects.text import Email
from app.domain.value_objects.raw_password import RawPassword
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)


class CreateUserRequestPydantic(BaseModel):
    """Request model for user creation with validation rules."""

    model_config = ConfigDict(frozen=True)

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Username must be between 3 and 50 characters, containing only letters, numbers, underscores, and hyphens",
    )
    email: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="Valid email address",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be between 8 and 128 characters",
    )
    user_type: UserRole = Field(
        default=UserRole.VIEWER,
        description="User type (VIEWER, STREAMER)",
    )


def create_user_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        description=getdoc(CreateUserInteractor),
        error_map={
            AuthenticationError: rule(
                status=status.HTTP_401_UNAUTHORIZED,
                on_error=log_info,
            ),
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: rule(
                status=status.HTTP_403_FORBIDDEN,
                on_error=log_info,
            ),
            DomainFieldError: rule(
                status=status.HTTP_400_BAD_REQUEST,
                on_error=log_info,
            ),
            RoleAssignmentNotPermittedError: rule(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                on_error=log_info,
            ),
            UsernameAlreadyExistsError: rule(
                status=status.HTTP_409_CONFLICT,
                on_error=log_info,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def create_user(
        request_data_pydantic: CreateUserRequestPydantic,
        interactor: FromDishka[CreateUserInteractor],
    ) -> CreateUserResponse:
        # Pre-validate value objects before creating request
        try:
            Username(request_data_pydantic.username)
            Email(request_data_pydantic.email)
            RawPassword(request_data_pydantic.password)
        except DomainFieldError as e:
            raise DomainFieldError(f"Invalid input: {str(e)}")

        request_data = CreateUserRequest(
            username=request_data_pydantic.username,
            email=request_data_pydantic.email,
            password=request_data_pydantic.password,
            user_type=request_data_pydantic.user_type,
        )
        return await interactor.execute(request_data)

    return router
