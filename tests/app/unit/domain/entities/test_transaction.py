from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.domain.base import DomainError
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.wallet.value_objects import WalletId
from tests.app.unit.factories.transaction import (
    create_amount,
    create_created_at,
    create_reference_id,
    create_transaction,
    create_transaction_id,
    create_wallet_id,
)


def test_transaction_initialization_sets_fields() -> None:
    created_at = create_created_at(datetime(2024, 1, 1, tzinfo=timezone.utc))
    amount = create_amount(Decimal("50.00"))
    reference_id = create_reference_id()
    from_wallet = create_wallet_id()
    to_wallet = create_wallet_id()
    transaction_id = create_transaction_id()
    metadata = {"note": "transfer"}

    transaction = create_transaction(
        transaction_id=transaction_id,
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        from_wallet_id=from_wallet,
        to_wallet_id=to_wallet,
        reference_id=reference_id,
        created_at=created_at,
        metadata=metadata,
    )

    assert transaction.id_ == transaction_id
    assert transaction.transaction_type is TransactionType.DEPOSIT
    assert transaction.amount == amount
    assert transaction.from_wallet_id == from_wallet
    assert transaction.to_wallet_id == to_wallet
    assert transaction.reference_id == reference_id
    assert transaction.created_at == created_at
    assert transaction.metadata == metadata


@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(Decimal("0"), id="zero"),
        pytest.param(Decimal("-1"), id="negative"),
    ],
)
def test_rejects_non_positive_amount(amount: Decimal) -> None:
    with pytest.raises(DomainError):
        create_transaction(amount=create_amount(amount))

@pytest.mark.parametrize(
    "wallet_id",
    [
        pytest.param(None, id="none"),
        pytest.param(create_wallet_id(), id="valid"),
    ],
)
def test_rejects_same_wallet_ids(wallet_id: WalletId | None) -> None:
    with pytest.raises(DomainError):
        create_transaction(from_wallet_id=wallet_id, to_wallet_id=wallet_id)
