from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.domain.base import DomainError
from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.transaction.transaction import Transaction
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.entities.transaction.value_objects import Allocation
from app.domain.shared.enums import ProductType
from app.domain.shared.value_objects.time import CreatedAt
from tests.app.unit.factories.ledger_entries import create_balanced_ledger_entries
from tests.app.unit.factories.value_objects import (
    create_id,
    create_reference_id,
    create_token,
    create_transaction_id,
)


def test_transaction_initialization_sets_fields() -> None:
    created_at = CreatedAt(datetime(2024, 1, 1, tzinfo=timezone.utc))
    amount = create_token(Decimal("50.00"))
    reference_id = create_reference_id()
    payer_id = create_id()
    transaction_id = create_transaction_id()
    ledger_entries = create_balanced_ledger_entries(
        amount=amount,
        debit_account_type=AccountType.USER_WALLET,
        credit_account_type=AccountType.ESCROW,
    )
    allocations = [
        Allocation(
            payee_type=AccountType.ESCROW,
            payee_id=None,
            amount=amount,
        )
    ]
    metadata = {"note": "escrow lock"}

    transaction = Transaction(
        id_=transaction_id,
        transaction_type=TransactionType.DEPOSIT,
        payer_type=AccountType.USER_WALLET,
        payer_id=payer_id,
        allocations=allocations,
        amount=amount,
        reference_id=reference_id,
        reference_type=ProductType.CHALLENGE,
        metadata=metadata,
        ledger_entries=ledger_entries,
        created_at=created_at,
    )

    assert transaction.id_ == transaction_id
    assert transaction.transaction_type is TransactionType.DEPOSIT
    assert transaction.payer_type == AccountType.USER_WALLET
    assert transaction.payer_id == payer_id
    assert transaction.allocations == allocations
    assert transaction.amount == amount
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
        Transaction(
            id_=create_transaction_id(),
            transaction_type=TransactionType.DEPOSIT,
            payer_type=AccountType.USER_WALLET,
            payer_id=create_id(),
            allocations=[
                Allocation(
                    payee_type=AccountType.ESCROW,
                    payee_id=None,
                    amount=create_token(amount),
                )
            ],
            amount=create_token(amount),
            reference_id=create_reference_id(),
            reference_type=ProductType.CHALLENGE,
            ledger_entries=create_balanced_ledger_entries(
                amount=create_token(abs(amount)),
                debit_account_type=AccountType.USER_WALLET,
                credit_account_type=AccountType.ESCROW,
            ),
            created_at=CreatedAt(datetime(2024, 1, 1, tzinfo=timezone.utc)),
        )


def test_rejects_allocation_total_mismatch() -> None:
    amount = create_token(Decimal("10.00"))
    with pytest.raises(DomainError):
        Transaction(
            id_=create_transaction_id(),
            transaction_type=TransactionType.DEPOSIT,
            payer_type=AccountType.USER_WALLET,
            payer_id=create_id(),
            allocations=[
                Allocation(
                    payee_type=AccountType.ESCROW,
                    payee_id=None,
                    amount=create_token(Decimal("5.00")),
                )
            ],
            amount=amount,
            reference_id=create_reference_id(),
            reference_type=ProductType.CHALLENGE,
            ledger_entries=create_balanced_ledger_entries(
                amount=amount,
                debit_account_type=AccountType.USER_WALLET,
                credit_account_type=AccountType.ESCROW,
            ),
            created_at=CreatedAt(datetime(2024, 1, 1, tzinfo=timezone.utc)),
        )
