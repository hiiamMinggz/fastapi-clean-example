from sqlalchemy import UUID, Column, DateTime, Enum, Numeric, Table
from sqlalchemy.orm import composite, relationship

from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.transaction.transaction import Transaction
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.enums import ProductType
from app.domain.shared.value_objects.id import ProductId, TransactionId, WalletId
from app.domain.shared.value_objects.time import CreatedAt
from app.domain.shared.value_objects.token import Token
from app.infrastructure.persistence_sqla.mappings.ledger_entry import (
    ledger_entries_table,
)
from app.infrastructure.persistence_sqla.registry import mapping_registry

transactions_table = Table(
    "transactions",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "transaction_type",
        Enum(TransactionType, name="transaction_type"),
        nullable=False,
    ),
    Column("payer_type", Enum(AccountType, name="account_type"), nullable=False),
    Column("payer_id", UUID(as_uuid=True), nullable=True),
    Column("amount", Numeric(12, 2), nullable=False),
    Column("reference_id", UUID(as_uuid=True), nullable=False),
    Column("reference_type", Enum(ProductType, name="product_type"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


def map_transactions_table() -> None:
    mapping_registry.map_imperatively(
        Transaction,
        transactions_table,
        properties={
            "id_": composite(TransactionId, transactions_table.c.id),
            "transaction_type": transactions_table.c.transaction_type,
            "payer_type": transactions_table.c.payer_type,
            "payer_id": composite(WalletId, transactions_table.c.payer_id),
            "amount": composite(Token, transactions_table.c.amount),
            "reference_id": composite(ProductId, transactions_table.c.reference_id),
            "reference_type": transactions_table.c.reference_type,
            "created_at": composite(CreatedAt, transactions_table.c.created_at),
            "_ledger_entries": relationship(
                "LedgerEntry",
                collection_class=list,
                cascade="all, delete-orphan",
                primaryjoin=transactions_table.c.id
                == ledger_entries_table.c.transaction_id,  # type: ignore[arg-type]
            ),
        },
        column_prefix="_",
    )
