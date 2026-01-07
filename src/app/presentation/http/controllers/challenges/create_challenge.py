from inspect import getdoc
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.commands.challenge.create_challenge import (
    CreateChallengeInteractor,
    CreateChallengeRequest,
    CreateChallengeResponse,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.base import DomainError
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)

def create_challenge_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        description=getdoc(CreateChallengeInteractor),
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
    async def create_challenge(
        request_data: CreateChallengeRequest,
        interactor: FromDishka[CreateChallengeInteractor],
    ) -> CreateChallengeResponse:
        request_data = CreateChallengeRequest(
            title=request_data.title,
            description=request_data.description,
            created_by=request_data.created_by,
            assigned_to=request_data.assigned_to,
            amount=request_data.amount,
            expires_at=request_data.expires_at,
        )
        return await interactor.execute(request_data)

    return router