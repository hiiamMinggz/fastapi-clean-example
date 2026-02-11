from typing import Tuple

from app.domain.base import DomainError, Entity
from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.ledger.ledger_entry import LedgerEntry
from app.domain.shared.entities.transaction.value_objects import Allocation
from app.domain.shared.enums import ProductType
from app.domain.shared.value_objects.time import CreatedAt
from app.domain.shared.value_objects.token import Token
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.value_objects.id import ProductId, TransactionId, WalletId


class Transaction(Entity[TransactionId]):
    def __init__(
        self,
        *,
        id_: TransactionId,
        transaction_type: TransactionType,
        payer_type: AccountType,
        payer_id: WalletId | None,
        allocations: Tuple[Allocation, ...],
        amount: Token,
        reference_id: ProductId,
        reference_type: ProductType,
        ledger_entries: Tuple[LedgerEntry, ...],
        created_at: CreatedAt,
    ) -> None:
        super().__init__(id_=id_)
        self.transaction_type = transaction_type
        self.payer_type = payer_type
        self.payer_id = payer_id
        self.allocations = allocations
        self.amount = amount
        self.reference_id = reference_id
        self.reference_type = reference_type
        self.ledger_entries = ledger_entries
        self.created_at = created_at
        self.validate()

    def validate(self) -> None:
        self._validate_payer()
        self._validate_amount()
        self._validate_allocations()
        self._validate_ledger_entries()
        self._validate_ledger_balance()
        self._validate_allocation_ledger_mapping()

    def _validate_amount(self) -> None:
        if self.amount.value <= Token.ZERO:
            raise DomainError(
                f"Transaction amount must be greater than 0, but got {self.amount}.",
            )

    def _validate_ledger_entries(self) -> None:
        if not self.ledger_entries or len(self.ledger_entries) < 2:
            raise DomainError(
                "Transaction must have at least two ledger entries.",
            )
    
    def _validate_ledger_balance(self) -> None:
        total_debit = sum(entry.debit.value for entry in self.ledger_entries)
        total_credit = sum(entry.credit.value for entry in self.ledger_entries)

        if total_debit != total_credit:
            raise DomainError(
                f"Ledger entries are not balanced: total debit {total_debit} != total credit {total_credit}.",
            )
        if total_debit != self.amount.value or total_credit != self.amount.value:
            raise DomainError(
                f"Transaction amount {self.amount} does not match ledger entries debit {total_debit} and credit {total_credit}.",
            )
    
    def _validate_payer(self) -> None:
        if self.payer_type == AccountType.USER_WALLET and self.payer_id is None:
            raise DomainError(
                "Payer must include wallet id for user wallets.",
            )
        if self.payer_type != AccountType.USER_WALLET and self.payer_id is not None:
            raise DomainError(
                "Payer id must be None for system accounts.",
            )

    def _validate_allocations(self) -> None:
        if not self.allocations:
            raise DomainError(
                "Transaction must have at least one allocation.",
            )
        total_allocations = sum(
            allocation.amount.value for allocation in self.allocations
        )
        if total_allocations != self.amount.value:
            raise DomainError(
                f"Transaction amount {self.amount} does not match allocations total {total_allocations}.",
            )

    def _validate_allocation_ledger_mapping(self) -> None:
        debits = [
            entry
            for entry in self.ledger_entries
            if entry.debit.value > Token.ZERO
        ]
        credits = [
            entry
            for entry in self.ledger_entries
            if entry.credit.value > Token.ZERO
        ]

        if len(debits) != 1:
            raise DomainError("Transaction must have exactly one debit entry.")

        debit_entry = debits[0]
        if (
            debit_entry.account_type != self.payer_type
            or debit_entry.account_id != self.payer_id
        ):
            raise DomainError(
                "Payer does not match debit ledger entry.",
            )
        if debit_entry.debit.value != self.amount.value:
            raise DomainError(
                "Debit entry amount does not match transaction amount.",
            )

        allocation_map: dict[tuple[AccountType, WalletId | None], Token] = {}
        for allocation in self.allocations:
            key = (allocation.payee_type, allocation.payee_id)
            allocation_map[key] = allocation_map.get(key, Token.ZERO) + allocation.amount.value

        credit_map: dict[tuple[AccountType, WalletId | None], Token] = {}
        for entry in credits:
            key = (entry.account_type, entry.account_id)
            credit_map[key] = credit_map.get(key, Token.ZERO) + entry.credit.value

        if credit_map != allocation_map:
            raise DomainError(
                "Allocations do not match credit ledger entries.",
            )
