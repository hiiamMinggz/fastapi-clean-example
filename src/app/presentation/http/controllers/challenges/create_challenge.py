from inspect import getdoc
from datetime import datetime

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict

from app.application.commands.create_challenge import (
    CreateChallengeInteractor,
    CreateChallengeRequest,
    CreateChallengeResponse,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.enums.fee import Fee
from app.domain.enums.challenge_status import Status
from app.domain.exceptions.base import DomainError
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)
from uuid import UUID

class CreateChallengeRequestPydantic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    description: str | None = None
    created_by: UUID
    assigned_to: UUID
    amount: str
    fee: Fee
    streamer_fixed_amount: str
    expires_at: datetime


def create_create_challenge_router() -> APIRouter:
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
        request_data_pydantic: CreateChallengeRequestPydantic,
        interactor: FromDishka[CreateChallengeInteractor],
    ) -> CreateChallengeResponse:
        current_time = datetime.now()
        request_data = CreateChallengeRequest(
            title=request_data_pydantic.title,
            description=request_data_pydantic.description,
            created_by=request_data_pydantic.created_by,
            assigned_to=request_data_pydantic.assigned_to,
            amount=request_data_pydantic.amount,
            fee=request_data_pydantic.fee,
            streamer_fixed_amount=request_data_pydantic.streamer_fixed_amount,
            status=Status.PENDING,  # Always PENDING when created
            created_at=current_time,  # Set to current time
            expires_at=request_data_pydantic.expires_at,
            accepted_at=None,  # Initially None as it's not accepted yet
        )
        return await interactor.execute(request_data)

    return router