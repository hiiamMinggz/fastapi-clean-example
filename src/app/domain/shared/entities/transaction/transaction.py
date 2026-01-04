from typing import List
from app.domain.base import DomainError, Entity
from app.domain.shared.entities.ledger.ledger_entry import LedgerEntry
from app.domain.shared.value_objects.time import CreatedAt
from app.domain.shared.entities.transaction.value_objects import TransactionId, ReferenceId
from app.domain.shared.value_objects.token import Token
from app.domain.shared.entities.transaction.transaction_type import TransactionType


class Transaction(Entity[TransactionId]):
    def __init__(
        self,
        *,
        id_: TransactionId,
        transaction_type: TransactionType,
        amount: Token,
        reference_id: ReferenceId,
        ledger_entries: List[LedgerEntry],
        metadata: dict,
        created_at: CreatedAt,
    ) -> None:
        super().__init__(id_=id_)
        self.transaction_type = transaction_type
        self.amount = amount
        self.reference_id = reference_id
        self.ledger_entries = ledger_entries
        self.metadata = metadata
        self.created_at = created_at
        self.validate()

    def validate(self) -> None:
        self._validate_amount()
        self._validate_ledger_entries()
        self._validate_ledger_balance()

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
    
