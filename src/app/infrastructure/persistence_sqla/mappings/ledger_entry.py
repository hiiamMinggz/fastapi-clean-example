from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, Numeric, Table
from sqlalchemy.orm import composite

from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.ledger.ledger_entry import LedgerEntry
from app.domain.shared.entities.ledger.value_objects import AccountId, EntryId
from app.domain.shared.entities.transaction.value_objects import TransactionId
from app.domain.shared.value_objects.time import CreatedAt
from app.domain.shared.value_objects.token import Token
from app.infrastructure.persistence_sqla.registry import mapping_registry

ledger_entries_table = Table(
    "ledger_entries",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "transaction_id",
        UUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("account_type", Enum(AccountType, name="account_type"), nullable=False),
    Column("account_id", UUID(as_uuid=True), nullable=True),
    Column("debit", Numeric(12, 2), default=0, nullable=False),
    Column("credit", Numeric(12, 2), default=0, nullable=False),
)


def map_ledger_entries_table() -> None:
    mapping_registry.map_imperatively(
        LedgerEntry,
        ledger_entries_table,
        properties={
            "id_": composite(EntryId, ledger_entries_table.c.id),
            "transaction_id": composite(
                TransactionId,
                ledger_entries_table.c.transaction_id,
            ),
            "account_type": ledger_entries_table.c.account_type,
            "account_id": composite(AccountId, ledger_entries_table.c.account_id),
            "debit": composite(Token, ledger_entries_table.c.debit),
            "credit": composite(Token, ledger_entries_table.c.credit),
        },
        column_prefix="_",
    )
