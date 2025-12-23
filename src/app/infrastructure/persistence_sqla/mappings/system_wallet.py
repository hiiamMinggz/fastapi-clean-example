from sqlalchemy import UUID, Column, Table, NUMERIC, DateTime, String
from sqlalchemy.orm import composite

from app.domain.entities.system_wallet import SystemWallet
from app.domain.user.value_objects import UserId
from app.domain.value_objects.token import Balance
from app.domain.user.value_objects import Username
from app.domain.value_objects.time import CreatedAt, UpdatedAt
from app.infrastructure.persistence_sqla.registry import mapping_registry

system_wallets_table = Table(
    "system_wallets",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String(Username.MAX_LEN), nullable=False, unique=True),
    Column("balance", NUMERIC(12, 2), default=0, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def map_system_wallets_table() -> None:
    mapping_registry.map_imperatively(
        SystemWallet,
        system_wallets_table,
        properties={
            "id_": composite(UserId, system_wallets_table.c.id),
            "name": composite(Username, system_wallets_table.c.name),
            "balance": composite(Balance, system_wallets_table.c.balance),
            "created_at": composite(CreatedAt, system_wallets_table.c.created_at),
            "updated_at": composite(UpdatedAt, system_wallets_table.c.updated_at),
        },
        column_prefix="_",
    )
