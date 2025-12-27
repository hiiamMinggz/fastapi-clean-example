from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
import uuid6

from app.domain.shared.entities.transaction.transaction import Transaction
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.entities.transaction.value_objects import (
    ReferenceId,
    TransactionId,
)
from app.domain.shared.value_objects.time import CreatedAt
from app.domain.shared.value_objects.token import Token
from app.domain.wallet.value_objects import WalletId


def create_transaction_id(value: UUID | None = None) -> TransactionId:
    return TransactionId(value or uuid6.uuid7())


def create_reference_id(value: UUID | None = None) -> ReferenceId:
    return ReferenceId(value or uuid6.uuid7())


def create_wallet_id(value: UUID | None = None) -> WalletId:
    return WalletId(value or uuid6.uuid7())


def create_amount(value: Decimal = Decimal("10.00")) -> Token:
    return Token(value)


def create_created_at(value: datetime | None = None) -> CreatedAt:
    return CreatedAt(value or datetime.now(timezone.utc))


def create_transaction(
    *,
    transaction_id: TransactionId | None = None,
    transaction_type: TransactionType = TransactionType.TRANSFER,
    amount: Token | None = None,
    from_wallet_id: WalletId | None = None,
    to_wallet_id: WalletId | None = None,
    reference_id: ReferenceId | None = None,
    created_at: CreatedAt | None = None,
    metadata: dict | None = None,
) -> Transaction:
    return Transaction(
        id_=transaction_id or create_transaction_id(),
        transaction_type=transaction_type,
        amount=amount or create_amount(),
        from_wallet_id=from_wallet_id,
        to_wallet_id=to_wallet_id,
        reference_id=reference_id or create_reference_id(),
        created_at=created_at or create_created_at(),
        metadata=metadata or {},
    )
