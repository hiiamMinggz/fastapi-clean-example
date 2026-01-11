from inspect import getdoc
from typing import Annotated
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, Security, status
from fastapi.params import Body
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.commands.challenge.toggle_challenge_status import (
    ToggleChallengeStatusInteractor,
    ToggleChallengeStatusRequest,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.base import DomainError
from app.domain.challenge.challenge_status import ChallengeStatus
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)

def toggle_challenge_status_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.patch(
        "/{challenge_id}/toggle-status",
        description=getdoc(ToggleChallengeStatusInteractor),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DomainError: status.HTTP_400_BAD_REQUEST,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def toggle_challenge_status(
        challenge_id: Annotated[str, Path()],
        status: Annotated[ChallengeStatus, Body()],
        interactor: FromDishka[ToggleChallengeStatusInteractor],
    ) -> None:
        request_data = ToggleChallengeStatusRequest(
            challenge_id=challenge_id,
            status=status,
        )
        return await interactor.execute(request_data)

    return router