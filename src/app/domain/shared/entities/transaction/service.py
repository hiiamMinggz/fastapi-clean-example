from datetime import datetime, timezone
from typing import Tuple

from app.domain.shared.entities.ledger.service import LedgerService
from app.domain.shared.entities.transaction.transaction import Transaction
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.entities.transaction.value_objects import Allocation
from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.shared.value_objects.token import Token
from app.domain.shared.value_objects.time import CreatedAt

from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.enums import ProductType
from app.domain.shared.value_objects.id import ProductId, TransactionId, WalletId

class TransactionService:
    def __init__(self, transaction_id_generator: IdGenerator, ledger_service: LedgerService):
        self._transaction_id_generator = transaction_id_generator
        self._ledger_service = ledger_service

    def create_escrow_release_transaction(
        self,
        *,
        allocations: Tuple[Allocation, ...],
        amount: Token,
        reference_id: ProductId,
        reference_type: ProductType,
    )-> Transaction:
        """creates a new Transaction instance"""
        transaction_id = TransactionId(self._transaction_id_generator())
        now = datetime.now(timezone.utc)

        escrow_debit_entry = self._ledger_service.create_escrow_debit_entry(
            debit=amount,
        )
        payee_credit_entries = [
            self._ledger_service.create_credit_entry(
                account_type=allocation.payee_type,
                account_id=allocation.payee_id,
                credit=allocation.amount,
            )
            for allocation in allocations
        ]
        ledger_entries = (escrow_debit_entry, *payee_credit_entries)
        
        transaction = Transaction(
            id_=transaction_id,
            transaction_type=TransactionType.ESCROW_RELEASE,
            payer_type=AccountType.ESCROW,
            payer_id=None,
            allocations=allocations,
            amount=amount,
            reference_id=reference_id,
            reference_type=reference_type,
            ledger_entries=ledger_entries,
            created_at=CreatedAt(now),
        )
        return transaction
    
    def create_escrow_lock_transaction(
        self,
        *,
        payer_id: WalletId,
        amount: Token,
        reference_id: ProductId,
        reference_type: ProductType,
    )-> Transaction:
        """creates a new Transaction instance"""
        transaction_id = TransactionId(self._transaction_id_generator())
        now = datetime.now(timezone.utc)
        
        allocation = Allocation(
            payee_type=AccountType.ESCROW,
            payee_id=None,
            amount=amount,
        )
        allocations = (allocation,)
        
        payer_debit_entry = self._ledger_service.create_user_wallet_debit_entry(
            account_id=payer_id,
            debit=amount,
        )
        escrow_credit_entry = self._ledger_service.create_escrow_credit_entry(
            credit=amount,
        )
        ledger_entries = (payer_debit_entry, escrow_credit_entry)
        
        transaction = Transaction(
            id_=transaction_id,
            transaction_type=TransactionType.ESCROW_LOCK,
            payer_type=AccountType.USER_WALLET,
            payer_id=payer_id,
            allocations=allocations,
            amount=amount,
            reference_id=reference_id,
            reference_type=reference_type,
            ledger_entries=ledger_entries,
            created_at=CreatedAt(now),
        )
        return transaction
    
    def create_transfer_transaction(
        self,
        *,
        payer_id: WalletId,
        allocations: Tuple[Allocation, ...],
        amount: Token,
        reference_id: ProductId,
        reference_type: ProductType,
    ) -> Transaction:
        """creates a new Transaction instance"""
        transaction_id = TransactionId(self._transaction_id_generator())
        now = datetime.now(timezone.utc)
        
        payer_debit_entry = self._ledger_service.create_user_wallet_debit_entry(
            account_id=payer_id,
            debit=amount,
        )
        payee_credit_entries = [
            self._ledger_service.create_credit_entry(
                account_type=allocation.payee_type,
                account_id=allocation.payee_id,
                credit=allocation.amount,
            )
            for allocation in allocations
        ]
        ledger_entries = (payer_debit_entry, *payee_credit_entries)
        
        transaction = Transaction(
            id_=transaction_id,
            transaction_type=TransactionType.TRANSFER,
            payer_type=AccountType.USER_WALLET,
            payer_id=payer_id,
            allocations=allocations,
            amount=amount,
            reference_id=reference_id,
            reference_type=reference_type,
            ledger_entries=ledger_entries,
            created_at=CreatedAt(now),
        )
        return transaction
    
    def create_withdraw_transaction(
        self,
        *,
        payer_id: WalletId,
        allocations: Tuple[Allocation, ...],
        amount: Token,
        reference_id: ProductId,
        reference_type: ProductType,
    )-> Transaction:
        """creates a new Transaction instance"""
        transaction_id = TransactionId(self._transaction_id_generator())
        now = datetime.now(timezone.utc)
        
        payer_debit_entry = self._ledger_service.create_user_wallet_debit_entry(
            account_id=payer_id,
            debit=amount,
        )
        payee_credit_entries = [
            self._ledger_service.create_credit_entry(
                account_type=allocation.payee_type,
                account_id=allocation.payee_id,
                credit=allocation.amount,
            )
            for allocation in allocations
        ]
        ledger_entries = (payer_debit_entry, *payee_credit_entries)
        
        transaction = Transaction(
            id_=transaction_id,
            transaction_type=TransactionType.WITHDRAW,
            payer_type=AccountType.USER_WALLET,
            payer_id=payer_id,
            allocations=allocations,
            amount=amount,
            reference_id=reference_id,
            reference_type=reference_type,
            ledger_entries=ledger_entries,
            created_at=CreatedAt(now),
        )
        return transaction
    
    def create_deposit_transaction(
        self,
        *,
        allocations: Tuple[Allocation, ...],
        amount: Token,
        reference_id: ProductId,
        reference_type: ProductType,
    )-> Transaction:
        """creates a new Transaction instance"""
        transaction_id = TransactionId(self._transaction_id_generator())
        now = datetime.now(timezone.utc)
        
        payer_debit_entry = self._ledger_service.create_bank_debit_entry(
            debit=amount,
        )
        payee_credit_entries = [
            self._ledger_service.create_credit_entry(
                account_type=allocation.payee_type,
                account_id=allocation.payee_id,
                credit=allocation.amount,
            )
            for allocation in allocations
        ]
        ledger_entries = (payer_debit_entry, *payee_credit_entries)
        
        transaction = Transaction(
            id_=transaction_id,
            transaction_type=TransactionType.DEPOSIT,
            payer_type=AccountType.BANK,
            payer_id=None,
            allocations=allocations,
            amount=amount,
            reference_id=reference_id,
            reference_type=reference_type,
            ledger_entries=ledger_entries,
            created_at=CreatedAt(now),
        )
        return transaction
