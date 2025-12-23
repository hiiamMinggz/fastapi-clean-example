from typing import TypedDict
from uuid import UUID

from app.domain.user.user_role import UserRole


class UserQueryModel(TypedDict):
    id_: UUID
    username: str
    role: UserRole
    is_active: bool
