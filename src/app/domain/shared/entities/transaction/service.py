from datetime import datetime, timezone
from app.domain.shared.entities.transaction.transaction import Transaction
from app.domain.shared.entities.transaction.transaction_type import TransactionType
from app.domain.shared.entities.transaction.value_objects import ReferenceId, TransactionId
from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.shared.value_objects.token import Token
from app.domain.shared.value_objects.time import CreatedAt
from app.domain.wallet.value_objects import WalletId


class TransactionService:
    def __init__(self, transaction_id_generator: IdGenerator):
        self._transaction_id_generator = transaction_id_generator

    def create_transaction(
        self,
        *,
        transaction_type: TransactionType,
        amount: Token,
        from_wallet_id: WalletId | None,
        to_wallet_id: WalletId | None,
        reference_id: ReferenceId,
        metadata: dict
    ) -> Transaction:
        transaction_id = TransactionId(self._transaction_id_generator())
        now = datetime.now(timezone.utc)
        
        transaction = Transaction(
            id_=transaction_id,
            transaction_type=transaction_type,
            amount=amount,
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
            reference_id=reference_id,
            created_at=CreatedAt(now),
            metadata=metadata,
        )
        return transaction