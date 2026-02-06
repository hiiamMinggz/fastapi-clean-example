from decimal import Decimal

from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.ledger.ledger_entry import LedgerEntry
from app.domain.shared.value_objects.token import Token
from tests.app.unit.factories.value_objects import (
    create_account_id,
    create_entry_id,
    create_token,
)


def create_ledger_entry(
    *,
    account_type: AccountType,
    account_id,
    debit: Token,
    credit: Token,
) -> LedgerEntry:
    return LedgerEntry(
        id_=create_entry_id(),
        account_type=account_type,
        account_id=account_id,
        debit=debit,
        credit=credit,
    )


def create_debit_entry(
    *,
    account_type: AccountType = AccountType.USER_WALLET,
    account_id=None,
    amount: Token | None = None,
) -> LedgerEntry:
    amount = amount or create_token(Decimal("10.00"))
    return create_ledger_entry(
        account_type=account_type,
        account_id=account_id or create_account_id(),
        debit=amount,
        credit=Token(Token.ZERO),
    )


def create_credit_entry(
    *,
    account_type: AccountType = AccountType.BANK,
    account_id=None,
    amount: Token | None = None,
) -> LedgerEntry:
    amount = amount or create_token(Decimal("10.00"))
    return create_ledger_entry(
        account_type=account_type,
        account_id=account_id or create_account_id(),
        debit=Token(Token.ZERO),
        credit=amount,
    )


def create_balanced_ledger_entries(
    *,
    amount: Token | None = None,
    debit_account_type: AccountType = AccountType.USER_WALLET,
    credit_account_type: AccountType = AccountType.BANK,
    debit_account_id=None,
    credit_account_id=None,
) -> list[LedgerEntry]:
    amount = amount or create_token(Decimal("10.00"))
    debit_entry = create_debit_entry(
        account_type=debit_account_type,
        account_id=debit_account_id,
        amount=amount,
    )
    credit_entry = create_credit_entry(
        account_type=credit_account_type,
        account_id=credit_account_id,
        amount=amount,
    )
    return [debit_entry, credit_entry]
