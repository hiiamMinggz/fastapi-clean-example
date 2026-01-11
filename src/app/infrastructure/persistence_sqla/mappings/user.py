from sqlalchemy import UUID, Boolean, Column, Enum, LargeBinary, String, Table, NUMERIC, DateTime, DOUBLE_PRECISION
from sqlalchemy.orm import composite

from app.domain.shared.value_objects.time import CreatedAt, UpdatedAt
from app.domain.user.user import User
from app.domain.user.user_role import UserRole
from app.domain.user.value_objects import Credibility, Email, UserId, UserPasswordHash
from app.domain.user.value_objects import Username


from app.infrastructure.persistence_sqla.registry import mapping_registry

users_table = Table(
    "users",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("username", String(Username.MAX_LEN), nullable=False, unique=True),
    Column("email", String(Email.MAX_LEN), nullable=False, unique=True),
    Column("password_hash", LargeBinary, nullable=False),
    Column(
        "role",
        Enum(UserRole, name="role"),
        default=UserRole.VIEWER,
        nullable=False,
    ),
    Column("is_active", Boolean, default=False, nullable=False),
    Column("credibility", DOUBLE_PRECISION, default=5.0, nullable=False),
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
            "role": users_table.c.role,
            "is_active": users_table.c.is_active,
            "credibility": composite(Credibility, users_table.c.credibility),
            "created_at": composite(CreatedAt, users_table.c.created_at),
            "updated_at": composite(UpdatedAt, users_table.c.updated_at),
        },
        column_prefix="_",
    )
