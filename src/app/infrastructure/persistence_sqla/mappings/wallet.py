from sqlalchemy import UUID, Column, Table, NUMERIC, DateTime
from sqlalchemy.orm import composite

from app.domain.shared.value_objects.time import CreatedAt, UpdatedAt
from app.domain.wallet.value_objects import Balance
from app.domain.wallet.wallet import Wallet
from app.domain.user.value_objects import UserId
from app.domain.wallet.value_objects import WalletId

from app.infrastructure.persistence_sqla.registry import mapping_registry

wallets_table = Table(
    "wallets",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("owner_id", UUID(as_uuid=True), nullable=False),
    Column("balance", NUMERIC(12, 2), default=0, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def map_wallets_table() -> None:
    mapping_registry.map_imperatively(
        Wallet,
        wallets_table,
        properties={
            "id_": composite(WalletId, wallets_table.c.id),
            "owner_id": composite(UserId, wallets_table.c.owner_id),
            "balance": composite(Balance, wallets_table.c.balance),
            "created_at": composite(CreatedAt, wallets_table.c.created_at),
            "updated_at": composite(UpdatedAt, wallets_table.c.updated_at),
        },
        column_prefix="_",
    )
