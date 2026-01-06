from app.domain.base import Entity
from app.domain.user.user_role import UserRole
from app.domain.user.value_objects import (
    UserId,
    UserPasswordHash,
    Username,
    Email,
    Credibility,
)
from app.domain.shared.value_objects.time import CreatedAt, UpdatedAt

class User(Entity[UserId]):
    def __init__(
        self,
        *,
        id_: UserId,
        username: Username,
        email: Email,
        password_hash: UserPasswordHash,
        role: UserRole,
        is_active: bool,
        credibility: Credibility,
        created_at: CreatedAt,
        updated_at: UpdatedAt | None,
    ) -> None:
        super().__init__(id_=id_)
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.credibility = credibility
        self.created_at = created_at
        self.updated_at = updated_at
