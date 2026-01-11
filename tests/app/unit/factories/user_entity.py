from app.domain.user.user import User
from app.domain.user.user_role import UserRole
from app.domain.user.value_objects import (
    UserId,
    UserPasswordHash,
    Username,
    Email,
    Credibility,
)
from app.domain.shared.value_objects.time import CreatedAt, UpdatedAt

from tests.app.unit.factories.value_objects import (
    create_email,
    create_password_hash,
    create_id,
    create_username,
)
from datetime import datetime

def create_user(
    user_id: UserId | None = None,
    username: Username | None = None,
    email: Email | None = None,
    password_hash: UserPasswordHash | None = None,
    role: UserRole = UserRole.VIEWER,
    is_active: bool = True,
    credibility: Credibility | None = None,
    created_at: CreatedAt | None = None,
    updated_at: UpdatedAt = None,
) -> User:
    now = datetime.now()
    return User(
        id_=user_id or create_id(),
        username=username or create_username(),
        email=email or create_email(),
        password_hash=password_hash or create_password_hash(),
        role=role,
        is_active=is_active,
        credibility=credibility or Credibility(Credibility.MIN_CREDIBILITY),
        created_at=created_at or CreatedAt(now),
        updated_at=updated_at or UpdatedAt(now),
    )
