from app.domain.base import DomainError, Entity
from app.domain.shared.value_objects.time import CreatedAt
from app.domain.wallet.value_objects import WalletId
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
        from_wallet_id: WalletId | None,
        to_wallet_id: WalletId | None,
        reference_id: ReferenceId,
        created_at: CreatedAt,
        metadata: dict
    ) -> None:
        super().__init__(id_=id_)
        self.transaction_type = transaction_type
        self.amount = amount
        self.from_wallet_id = from_wallet_id
        self.to_wallet_id = to_wallet_id
        self.reference_id = reference_id
        self.created_at = created_at
        self.metadata = metadata
        self.validate()

    def validate(self) -> None:
        self._validate_amount(self.amount)
        self._validate_transaction_flow(self.from_wallet_id)

    def _validate_amount(self, amount_value: Token) -> None:
        if amount_value.value <= Token.ZERO:
            raise DomainError(
                f"Transaction amount must be greater than 0, but got {amount_value}.",
            )

    def _validate_transaction_direction(self) -> None:
        if self.from_wallet_id == self.to_wallet_id:
            raise DomainError("Transaction from_wallet_id must be different than to_wallet_id")
        
    def _validate_transaction_flow(self) -> None:
        if self.transaction_type in (TransactionType.DEPOSIT, TransactionType.WITHDRAW, TransactionType.ESCROW_RELEASE):
            if not isinstance(self.to_wallet_id, WalletId):
                raise DomainError("to_wallet_id must be of type WalletId.")
        elif self.transaction_type == TransactionType.TRANSFER:
            if not all(isinstance(id, WalletId) for id in (self.from_wallet_id, self.to_wallet_id)):
                raise DomainError("Both from_wallet_id and to_wallet_id must be of type WalletId.")
        elif self.transaction_type == TransactionType.ESCROW_LOCK:
            if not isinstance(self.from_wallet_id, WalletId):
                raise DomainError("from_wallet_id must be of type WalletId.")
        else:
            raise DomainError("Invalid transaction type.")
