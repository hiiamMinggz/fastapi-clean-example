from datetime import datetime, timezone
from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.ledger.ledger_entry import LedgerEntry
from app.domain.shared.entities.ledger.value_objects import AccountId, EntryId
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
        account_type: AccountType,
        account_id: AccountId | None,
        debit: Token,
        credit: Token,
    ) -> LedgerEntry:
        """creates a new Ledger instance"""
        entry_id = EntryId(self._ledger_entry_id_generator())
        
        entry = LedgerEntry(
            id_=entry_id,
            account_type=account_type,
            account_id=account_id,
            debit=debit,
            credit=credit,
        )
        return entry
    
    def create_bank_debit_entry(
        self,
        *,
        debit: Token,
    ) -> LedgerEntry:
        """creates a new Ledger instance"""
        entry_id = EntryId(self._ledger_entry_id_generator())        
        
        entry = LedgerEntry(
            id_=entry_id,
            account_type=AccountType.BANK,
            account_id=None,
            debit=debit,
            credit=Token(Token.ZERO),
        )
        return entry
    
    def create_escrow_debit_entry(
        self,
        *,
        debit: Token,
    ) -> LedgerEntry:
        """creates a new Ledger instance"""
        entry_id = EntryId(self._ledger_entry_id_generator())
        
        entry = LedgerEntry(
            id_=entry_id,
            account_type=AccountType.ESCROW,
            account_id=None,
            debit=debit,
            credit=Token(Token.ZERO),
        )
        return entry
    
    def create_escrow_credit_entry(
        self,
        *,
        credit: Token,
    ) -> LedgerEntry:
        """creates a new Ledger instance"""
        entry_id = EntryId(self._ledger_entry_id_generator())
        
        entry = LedgerEntry(
            id_=entry_id,
            account_type=AccountType.ESCROW,
            account_id=None,
            debit=Token(Token.ZERO),
            credit=credit,
        )
        return entry
    
    def create_user_wallet_debit_entry(
        self,
        *,
        account_id: AccountId,
        debit: Token,
    ) -> LedgerEntry:
        """creates a new Ledger instance"""
        entry_id = EntryId(self._ledger_entry_id_generator())
        
        entry = LedgerEntry(
            id_=entry_id,
            account_type=AccountType.USER_WALLET,
            account_id=account_id,
            debit=debit,
            credit=Token(Token.ZERO),
        )
        return entry
    
    def create_user_wallet_credit_entry(
        self,
        *,
        account_id: AccountId,
        credit: Token,
    ) -> LedgerEntry:
        """creates a new Ledger instance"""
        entry_id = EntryId(self._ledger_entry_id_generator())
        
        entry = LedgerEntry(
            id_=entry_id,
            account_type=AccountType.USER_WALLET,
            account_id=account_id,
            debit=Token(Token.ZERO),
            credit=credit,
        )
        return entry
    
    def create_commission_credit_entry(
        self,
        *,
        credit: Token,
    ) -> LedgerEntry:
        """creates a new Ledger instance"""
        entry_id = EntryId(self._ledger_entry_id_generator())
        
        entry = LedgerEntry(
            id_=entry_id,
            account_type=AccountType.COMMISSION,
            account_id=None,
            debit=Token(Token.ZERO),
            credit=credit,
        )
        return entry