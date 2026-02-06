from decimal import Decimal
from uuid import uuid4
from unittest.mock import MagicMock

from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.ledger.service import LedgerService
from app.domain.shared.value_objects.token import Token
from tests.app.unit.factories.value_objects import create_account_id, create_token


def test_create_ledger_entry_sets_fields(
    ledger_entry_id_generator: MagicMock,
) -> None:
    expected_id = uuid4()
    ledger_entry_id_generator.return_value = expected_id
    sut = LedgerService(ledger_entry_id_generator)
    account_id = create_account_id()
    debit = Token(Decimal("5.00"))
    credit = Token(Token.ZERO)

    entry = sut.create_ledger_entry(
        account_type=AccountType.USER_WALLET,
        account_id=account_id,
        debit=debit,
        credit=credit,
    )

    assert entry.id_.value == expected_id
    assert entry.account_type is AccountType.USER_WALLET
    assert entry.account_id == account_id
    assert entry.debit == debit
    assert entry.credit == credit
    ledger_entry_id_generator.assert_called_once()


def test_create_bank_debit_entry_sets_defaults(
    ledger_entry_id_generator: MagicMock,
) -> None:
    expected_id = uuid4()
    ledger_entry_id_generator.return_value = expected_id
    sut = LedgerService(ledger_entry_id_generator)
    debit = create_token(Decimal("12.00"))

    entry = sut.create_bank_debit_entry(debit=debit)

    assert entry.id_.value == expected_id
    assert entry.account_type is AccountType.BANK
    assert entry.account_id is None
    assert entry.debit == debit
    assert entry.credit == Token(Token.ZERO)
    ledger_entry_id_generator.assert_called_once()


def test_create_escrow_debit_entry_sets_defaults(
    ledger_entry_id_generator: MagicMock,
) -> None:
    expected_id = uuid4()
    ledger_entry_id_generator.return_value = expected_id
    sut = LedgerService(ledger_entry_id_generator)
    debit = create_token(Decimal("8.00"))

    entry = sut.create_escrow_debit_entry(debit=debit)

    assert entry.id_.value == expected_id
    assert entry.account_type is AccountType.ESCROW
    assert entry.account_id is None
    assert entry.debit == debit
    assert entry.credit == Token(Token.ZERO)
    ledger_entry_id_generator.assert_called_once()


def test_create_escrow_credit_entry_sets_defaults(
    ledger_entry_id_generator: MagicMock,
) -> None:
    expected_id = uuid4()
    ledger_entry_id_generator.return_value = expected_id
    sut = LedgerService(ledger_entry_id_generator)
    credit = create_token(Decimal("9.00"))

    entry = sut.create_escrow_credit_entry(credit=credit)

    assert entry.id_.value == expected_id
    assert entry.account_type is AccountType.ESCROW
    assert entry.account_id is None
    assert entry.debit == Token(Token.ZERO)
    assert entry.credit == credit
    ledger_entry_id_generator.assert_called_once()


def test_create_user_wallet_debit_entry_sets_defaults(
    ledger_entry_id_generator: MagicMock,
) -> None:
    expected_id = uuid4()
    ledger_entry_id_generator.return_value = expected_id
    sut = LedgerService(ledger_entry_id_generator)
    account_id = create_account_id()
    debit = create_token(Decimal("15.00"))

    entry = sut.create_user_wallet_debit_entry(
        account_id=account_id,
        debit=debit,
    )

    assert entry.id_.value == expected_id
    assert entry.account_type is AccountType.USER_WALLET
    assert entry.account_id == account_id
    assert entry.debit == debit
    assert entry.credit == Token(Token.ZERO)
    ledger_entry_id_generator.assert_called_once()


def test_create_user_wallet_credit_entry_sets_defaults(
    ledger_entry_id_generator: MagicMock,
) -> None:
    expected_id = uuid4()
    ledger_entry_id_generator.return_value = expected_id
    sut = LedgerService(ledger_entry_id_generator)
    account_id = create_account_id()
    credit = create_token(Decimal("22.00"))

    entry = sut.create_user_wallet_credit_entry(
        account_id=account_id,
        credit=credit,
    )

    assert entry.id_.value == expected_id
    assert entry.account_type is AccountType.USER_WALLET
    assert entry.account_id == account_id
    assert entry.debit == Token(Token.ZERO)
    assert entry.credit == credit
    ledger_entry_id_generator.assert_called_once()


def test_create_commission_credit_entry_sets_defaults(
    ledger_entry_id_generator: MagicMock,
) -> None:
    expected_id = uuid4()
    ledger_entry_id_generator.return_value = expected_id
    sut = LedgerService(ledger_entry_id_generator)
    credit = create_token(Decimal("7.50"))

    entry = sut.create_commission_credit_entry(credit=credit)

    assert entry.id_.value == expected_id
    assert entry.account_type is AccountType.COMMISSION
    assert entry.account_id is None
    assert entry.debit == Token(Token.ZERO)
    assert entry.credit == credit
    ledger_entry_id_generator.assert_called_once()
