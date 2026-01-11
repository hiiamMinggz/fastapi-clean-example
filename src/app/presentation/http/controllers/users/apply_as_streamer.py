from inspect import getdoc
from typing import Annotated
from decimal import Decimal
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel

from app.application.commands.user.apply_as_streamer import (
    ApplyAsStreamerInteractor,
    ApplyAsStreamerRequest,
    ApplyAsStreamerResponse,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.base import DomainFieldError
from app.domain.user.exceptions import (
    RoleAssignmentNotPermittedError,
    UserNotFoundByUserIdError,
)
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


class ApplyAsStreamerPayload(BaseModel):
    min_amount_challenge: Decimal
    disable_challenges: bool = False


def create_apply_as_streamer_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/apply-as-streamer",
        description=getdoc(ApplyAsStreamerInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            UserNotFoundByUserIdError: status.HTTP_404_NOT_FOUND,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def apply_as_streamer(
        request_data: ApplyAsStreamerRequest,
        interactor: FromDishka[ApplyAsStreamerInteractor],
    ) -> ApplyAsStreamerResponse:
        return await interactor.execute(request_data)

    return router
