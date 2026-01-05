from datetime import datetime, timezone
from typing import List
from app.domain.shared.entities.ledger.ledger_entry import LedgerEntry
from app.domain.shared.entities.transaction.transaction import Transaction
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.entities.transaction.value_objects import ReferenceId, TransactionId
from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.shared.value_objects.token import Token
from app.domain.shared.value_objects.time import CreatedAt


class TransactionService:
    def __init__(self, transaction_id_generator: IdGenerator):
        self._transaction_id_generator = transaction_id_generator

    def create_transaction(
        self,
        *,
        transaction_type: TransactionType,
        amount: Token,
        reference_id: ReferenceId,
        ledger_entries: List[LedgerEntry],
        metadata: dict,
    ) -> Transaction:
        transaction_id = TransactionId(self._transaction_id_generator())
        now = datetime.now(timezone.utc)
        
        transaction = Transaction(
            id_=transaction_id,
            transaction_type=transaction_type,
            amount=amount,
            reference_id=reference_id,
            ledger_entries=ledger_entries,
            created_at=CreatedAt(now),
            metadata=metadata,
        )
        return transaction