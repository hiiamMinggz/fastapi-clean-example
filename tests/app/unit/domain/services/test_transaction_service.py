from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.domain.base import DomainError
from app.domain.shared.entities.transaction.service import TransactionService
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.entities.transaction.value_objects import TransactionId
from app.domain.shared.value_objects.token import Token
from tests.app.unit.factories.transaction import (
    create_amount,
    create_reference_id,
    create_wallet_id,
)


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None) -> datetime:
        return cls.fixed_now


def _patch_datetime(monkeypatch: pytest.MonkeyPatch, fixed_now: datetime) -> None:
    FixedDateTime.fixed_now = fixed_now
    monkeypatch.setattr(
        "app.domain.shared.entities.transaction.service.datetime",
        FixedDateTime,
    )


def test_create_transaction_sets_fields(
    transaction_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_id = TransactionId(create_wallet_id().value)
    transaction_id_generator.return_value = expected_id.value
    sut = TransactionService(transaction_id_generator)
    fixed_now = datetime(2024, 2, 1, 12, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)
    transaction_type = TransactionType.TRANSFER
    amount = create_amount(Decimal("75.00"))
    from_wallet_id = create_wallet_id()
    to_wallet_id = create_wallet_id()
    reference_id = create_reference_id()
    metadata = {"reason": "payment"}

    transaction = sut.create_transaction(
        transaction_type=transaction_type,
        amount=amount,
        from_wallet_id=from_wallet_id,
        to_wallet_id=to_wallet_id,
        reference_id=reference_id,
        metadata=metadata,
    )

    assert transaction.id_ == expected_id
    assert transaction.transaction_type is transaction_type
    assert transaction.amount == amount
    assert transaction.from_wallet_id == from_wallet_id
    assert transaction.to_wallet_id == to_wallet_id
    assert transaction.reference_id == reference_id
    assert transaction.created_at.value == fixed_now
    assert transaction.metadata == metadata
    transaction_id_generator.assert_called_once()


def test_create_transaction_rejects_invalid_amount(
    transaction_id_generator: MagicMock,
) -> None:
    sut = TransactionService(transaction_id_generator)

    with pytest.raises(DomainError):
        sut.create_transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=Token(Decimal("0")),
            from_wallet_id=create_wallet_id(),
            to_wallet_id=create_wallet_id(),
            reference_id=create_reference_id(),
            metadata={},
        )

def test_create_transaction_rejects_same_wallet_ids(
    transaction_id_generator: MagicMock,
) -> None:
    sut = TransactionService(transaction_id_generator)
    wallet_id = create_wallet_id()

    with pytest.raises(DomainError):
        sut.create_transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=Token(Decimal("0")),
            from_wallet_id=wallet_id,
            to_wallet_id=wallet_id,
            reference_id=create_reference_id(),
            metadata={},
        )

