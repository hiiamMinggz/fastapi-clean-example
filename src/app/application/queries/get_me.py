import logging
from typing import TypedDict
from uuid import UUID

from app.application.common.services.current_user import CurrentUserService
from app.domain.user.user_role import UserRole

log = logging.getLogger(__name__)


class GetMeResponse(TypedDict):
    id_: UUID
    username: str
    email: str
    role: UserRole
    is_active: bool
    credibility: float


class GetMeQueryService:
    """
    - Open to authenticated users.
    - Returns the currently authenticated user's profile.
    """

    def __init__(self, current_user_service: CurrentUserService):
        self._current_user_service = current_user_service

    async def execute(self) -> GetMeResponse:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """
        log.info("Get me: started.")
        user = await self._current_user_service.get_current_user()
        response = GetMeResponse(
            id_=user.id_.value,
            username=user.username.value,
            email=user.email.value,
            role=user.role,
            is_active=user.is_active,
            credibility=user.credibility.value,
        )
        log.info("Get me: done.")
        return response
