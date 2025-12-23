from collections.abc import Mapping
from typing import Final

from app.domain.user.user_role import UserRole

SUBORDINATE_ROLES: Final[Mapping[UserRole, set[UserRole]]] = {
    UserRole.SUPER_ADMIN: {UserRole.STREAMER, UserRole.VIEWER},
}
