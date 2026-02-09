from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.domain.base import DomainError
from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.transaction.service import TransactionService
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.entities.transaction.value_objects import Allocation
from tests.app.unit.factories.ledger_entries import create_balanced_ledger_entries
from tests.app.unit.factories.value_objects import (
    create_id,
    create_reference_id,
    create_reference_type,
    create_token,
    create_transaction_id,
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
    expected_id = create_transaction_id()
    transaction_id_generator.return_value = expected_id.value
    fixed_now = datetime(2024, 2, 1, 12, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)
    sut = TransactionService(transaction_id_generator)
    transaction_type = TransactionType.TRANSFER
    payer = create_id()
    amount = create_token(Decimal("75.00"))
    reference_id = create_reference_id()
    reference_type = create_reference_type()
    ledger_entries = create_balanced_ledger_entries(amount=amount)

    transaction = sut.create_transaction(
        transaction_type=transaction_type,
        payer_type=AccountType.USER_WALLET,
        payer_id=payer,
        allocations=[
            Allocation(
                payee_type=AccountType.BANK,
                payee_id=None,
                amount=amount,
            )
        ],
        amount=amount,
        reference_id=reference_id,
        reference_type=reference_type,
        ledger_entries=ledger_entries,
    )

    assert transaction.id_ == expected_id
    assert transaction.transaction_type is transaction_type
    assert transaction.payer_type == AccountType.USER_WALLET
    assert transaction.payer_id == payer
    assert transaction.allocations[0].amount == amount
    assert transaction.amount == amount
    assert transaction.reference_id == reference_id
    assert transaction.reference_type == reference_type
    assert transaction.ledger_entries == ledger_entries
    assert transaction.created_at.value == fixed_now
    transaction_id_generator.assert_called_once()


def test_create_transaction_rejects_missing_payer_id_for_user_wallet(
    transaction_id_generator: MagicMock,
) -> None:
    sut = TransactionService(transaction_id_generator)

    with pytest.raises(DomainError):
        sut.create_transaction(
            transaction_type=TransactionType.DEPOSIT,
            payer_type=AccountType.USER_WALLET,
            payer_id=None,
            allocations=[
                Allocation(
                    payee_type=AccountType.BANK,
                    payee_id=None,
                    amount=create_token(Decimal("10.00")),
                )
            ],
            amount=create_token(Decimal("10.00")),
            reference_id=create_reference_id(),
            reference_type=create_reference_type(),
            ledger_entries=create_balanced_ledger_entries(
                amount=create_token(Decimal("10.00")),
            ),
        )
