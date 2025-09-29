from sqlalchemy import UUID, Boolean, Column, Enum, LargeBinary, String, Table, Integer, DateTime
from sqlalchemy.orm import composite

from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.value_objects.id import UserId
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username import Username
from app.domain.value_objects.text import Email
from app.domain.value_objects.credibility import Credibility
from app.domain.value_objects.token import Balance
from app.domain.value_objects.time import CreatedAt, UpdatedAt
from app.infrastructure.persistence_sqla.registry import mapping_registry

users_table = Table(
    "users",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("username", String(Username.MAX_LEN), nullable=False, unique=True),
    Column("email", String(Email.MAX_LEN), nullable=False, unique=True),
    Column("password_hash", LargeBinary, nullable=False),
    Column(
        "user_type",
        Enum(UserRole, name="userrole"),
        default=UserRole.VIEWER,
        nullable=False,
    ),
    Column("locked", Boolean, default=False, nullable=False),
    Column("credibility", Integer, default=100, nullable=False),
    Column("balance", Integer, default=0, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def map_users_table() -> None:
    mapping_registry.map_imperatively(
        User,
        users_table,
        properties={
            "id_": composite(UserId, users_table.c.id),
            "username": composite(Username, users_table.c.username),
            "email": composite(Email, users_table.c.email),
            "password_hash": composite(UserPasswordHash, users_table.c.password_hash),
            "user_type": users_table.c.user_type,
            "locked": users_table.c.locked,
            "credibility": composite(Credibility, users_table.c.credibility),
            "balance": composite(Balance, users_table.c.balance),
            "created_at": composite(CreatedAt, users_table.c.created_at),
            "updated_at": composite(UpdatedAt, users_table.c.updated_at),
        },
        column_prefix="_",
    )
