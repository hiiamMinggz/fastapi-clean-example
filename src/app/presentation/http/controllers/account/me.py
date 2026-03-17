from inspect import getdoc
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.queries.get_me import GetMeQueryService
from app.domain.user.user_role import UserRole
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


class MeResponse(BaseModel):
    id_: UUID
    username: str
    email: str
    role: UserRole
    is_active: bool
    credibility: float


def create_me_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/me",
        description=getdoc(GetMeQueryService),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def get_me(
        service: FromDishka[GetMeQueryService],
    ) -> MeResponse:
        result = await service.execute()
        return MeResponse(**result)

    return router
