from datetime import datetime, timezone
from app.domain.ledger.account_type import AccountType
from app.domain.ledger.ledger_entry import LedgerEntry
from app.domain.ledger.value_objects import AccountId, EntryId
from app.domain.shared.entities.transaction.value_objects import TransactionId
from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.shared.value_objects.time import CreatedAt
from app.domain.shared.value_objects.token import Token


class LedgerService:
    def __init__(self, ledger_entry_id_generator: IdGenerator):
        self._ledger_entry_id_generator = ledger_entry_id_generator

    def create_ledger_entry(
        self,
        *,
        transaction_id: TransactionId,
        account_type: AccountType,
        account_id: AccountId | None,
        debit: Token | None,
        credit: Token | None,
    ) -> LedgerEntry:
        """creates a new Ledger instance"""
        entry_id = EntryId(self._ledger_entry_id_generator())
        now = datetime.now(timezone.utc)
        
        entry = LedgerEntry(
            id_=entry_id,
            transaction_id=transaction_id,
            account_type=account_type,
            account_id=account_id,
            debit=debit,
            credit=credit,
            created_at=CreatedAt(now),
        )
        return entry
    
