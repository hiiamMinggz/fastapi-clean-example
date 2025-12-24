from datetime import datetime, timezone
from app.domain.user.user import User
from app.domain.user.user_role import UserRole

from app.domain.user.value_objects import (
    UserId,
    UserPasswordHash,
    Username,
    Email,
    Credibility,
    RawPassword
)
from app.domain.shared.value_objects.time import CreatedAt, UpdatedAt
from app.domain.user.ports import PasswordHasher
from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.user.exceptions import ActivationChangeNotPermittedError, RoleAssignmentNotPermittedError, RoleChangeNotPermittedError
class UserService:
    def __init__(
        self,
        user_id_generator: IdGenerator,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher

    def create_user(
        self,
        *,
        username: Username,
        raw_password: RawPassword,
        email: Email,
        role: UserRole,
    ) -> User:
        if not role.is_assignable:
            raise RoleAssignmentNotPermittedError(role)
        
        user_id = UserId(self._user_id_generator())
        password_hash = UserPasswordHash(self._password_hasher.hash(raw_password))

        now = datetime.now(timezone.utc)

        return User(
            id_=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
            credibility=Credibility(Credibility.MAX_CREDIBILITY),
            created_at=CreatedAt(now),
            updated_at=UpdatedAt(now),
        )

    def is_password_valid(self, user: User, *, raw_password: RawPassword) -> bool:
        return self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=user.password_hash.value,
        )

    def change_password(self, user: User, *, raw_password: RawPassword) -> None:
        hashed_password = UserPasswordHash(self._password_hasher.hash(raw_password))
        user.password_hash = hashed_password

    def toggle_user_activation(self, user: User, *, is_active: bool) -> None:
        if not user.role.is_changeable:
            raise ActivationChangeNotPermittedError(user.username, user.role)
        user.is_active = is_active
        
    def toggle_user_role(self, user: User, *, is_streamer: bool) -> None:
        if not user.role.is_changeable:
            raise RoleChangeNotPermittedError(user.username, user.role)
        if is_streamer:
            user.role = UserRole.STREAMER
        user.role = UserRole.VIEWER
        
