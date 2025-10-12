from inspect import getdoc
from typing import Annotated
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Path, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.commands.challenge.update_challenge import (
    UpdateChallengeInteractor,
    UpdateChallengeRequest,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.exceptions.base import DomainError
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)

def update_challenge_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.patch(
        "/{challenge_id}/update",
        description=getdoc(UpdateChallengeInteractor),
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
    async def update_challenge(
        request_data: UpdateChallengeRequest,
        interactor: FromDishka[UpdateChallengeInteractor],
    ) -> None:
        request_data = UpdateChallengeRequest(
            challenge_id=request_data.challenge_id,
            title=request_data.title,
            description=request_data.description,
            amount=request_data.amount,
            expires_at=request_data.expires_at,
        )
        return await interactor.execute(request_data)

    return router