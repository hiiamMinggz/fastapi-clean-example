from datetime import datetime, timezone
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole

from app.domain.enums.user_status import UserStatus
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.id_generator import IdGenerator
from app.domain.value_objects.credibility import Credibility
from app.domain.value_objects.raw_password import RawPassword
from app.domain.value_objects.id import UserId
from app.domain.value_objects.text import Email
from app.domain.value_objects.token import Balance
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username import Username
from app.domain.value_objects.time import CreatedAt, UpdatedAt

class UserService:
    def __init__(
        self,
        user_id_generator: IdGenerator,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher

    def create_viewer(
        self,
        username: Username,
        raw_password: RawPassword,
        email: Email,
    ) -> User:

        user_id = UserId(self._user_id_generator())
        password_hash = UserPasswordHash(self._password_hasher.hash(raw_password))
        user_type = UserRole.VIEWER
        staus = UserStatus.ACTIVE
        inited_credibility = Credibility(Credibility.MAX_CREDIBILITY)
        
        now = datetime.now(timezone.utc)
        created_at = CreatedAt(now)
        updated_at = UpdatedAt(now)
        
        return User(
            id_=user_id,
            username=username,
            password_hash=password_hash,
            email=email,
            user_type=user_type,
            locked=False,
            status=staus,
            credibility=inited_credibility,
            created_at=created_at,
            updated_at=updated_at,
        )
        
    def create_streamer(
        self,
        username: Username,
        raw_password: RawPassword,
        email: Email,
    ) -> User:

        user_id = UserId(self._user_id_generator())
        password_hash = UserPasswordHash(self._password_hasher.hash(raw_password))
        user_type = UserRole.STREAMER
        status = UserStatus.PENDING
        inited_credibility = Credibility(Credibility.MAX_CREDIBILITY)
        
        now = datetime.now(timezone.utc)
        created_at = CreatedAt(now)
        updated_at = UpdatedAt(now)
        
        return User(
            id_=user_id,
            username=username,
            password_hash=password_hash,
            email=email,
            user_type=user_type,
            locked=False,
            status=status,
            credibility=inited_credibility,
            created_at=created_at,
            updated_at=updated_at,
        )

    def is_password_valid(self, user: User, raw_password: RawPassword) -> bool:
        return self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=user.password_hash.value,
        )

    def change_password(self, user: User, raw_password: RawPassword) -> None:
        hashed_password = UserPasswordHash(self._password_hasher.hash(raw_password))
        user.password_hash = hashed_password

    def toggle_user_activation(self, user: User, *, locked: bool) -> None:
        user.locked = locked
        
    def toggle_user_role(self, user: User, *, is_streamer: bool) -> None:
        if is_streamer:
            user.user_type = UserRole.STREAMER
        else:
            user.user_type = UserRole.VIEWER
        
    def toggle_user_status(self, user: User, *, status: UserStatus) -> None:
        user.status = status
