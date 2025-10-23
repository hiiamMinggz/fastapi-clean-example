from app.domain.entities.base import Entity
from app.domain.enums.user_role import UserRole
from app.domain.enums.user_status import UserStatus
from app.domain.value_objects.id import UserId
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username import Username
from app.domain.value_objects.text import Email
from app.domain.value_objects.credibility import Credibility
from app.domain.value_objects.token import Balance
from app.domain.value_objects.time import CreatedAt, UpdatedAt

class User(Entity[UserId]):
    def __init__(
        self,
        *,
        id_: UserId,
        username: Username,
        email: Email,
        password_hash: UserPasswordHash,
        user_type: UserRole,
        locked: bool,
        status: UserStatus,
        credibility: Credibility,
        created_at: CreatedAt,
        updated_at: UpdatedAt,
    ) -> None:
        super().__init__(id_=id_)
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.user_type = user_type
        self.locked = locked
        self.status = status
        self.credibility = credibility
        self.created_at = created_at
        self.updated_at = updated_at
