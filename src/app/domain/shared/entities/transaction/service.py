from datetime import datetime, timezone
from typing import List
from weakref import ProductType
from app.domain.shared.entities.ledger.ledger_entry import LedgerEntry
from app.domain.shared.entities.transaction.transaction import Transaction
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.shared.value_objects.token import Token
from app.domain.shared.value_objects.time import CreatedAt

from app.domain.shared.value_objects.id import ProductId, TransactionId, UserId

class TransactionService:
    def __init__(self, transaction_id_generator: IdGenerator):
        self._transaction_id_generator = transaction_id_generator
    
    def create_transaction(
        self,
        *,
        transaction_type: TransactionType,
        payer: UserId | None,
        payee: UserId | None,
        amount: Token,
        reference_id: ProductId,
        reference_type: ProductType,
        ledger_entries: List[LedgerEntry],
    ) -> Transaction:
        """creates a new Transaction instance"""
        transaction_id = TransactionId(self._transaction_id_generator())
        now = datetime.now(timezone.utc)

        transaction = Transaction(
            id_=transaction_id,
            transaction_type=transaction_type,
            payer=payer,
            payee=payee,
            amount=amount,
            reference_id=reference_id,
            reference_type=reference_type,
            ledger_entries=ledger_entries,
            created_at=CreatedAt(now),
        )
        return transaction