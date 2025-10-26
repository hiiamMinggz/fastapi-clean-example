from decimal import Decimal

from app.domain.entities.wallet import Wallet
from app.domain.value_objects.id import UserId
from app.domain.value_objects.token import Balance, Token
from app.domain.value_objects.time import CreatedAt, UpdatedAt
from app.domain.exceptions.base import DomainError
from datetime import datetime, timezone
class WalletService:
    def __init__(self) -> None:
        pass
    
    def create_wallet(
        self,
        user_id: UserId
    ) -> Wallet:
        """creates a new Wallet instance"""
        inited_balance = Balance(Decimal("0.00"))
        now = datetime.now(timezone.utc)
        created_at = CreatedAt(now)
        updated_at = UpdatedAt(now)
        
        wallet = Wallet(
            id_=user_id,
            balance=inited_balance,
            created_at=created_at,
            updated_at=updated_at,
        )
        return wallet
    
    def credit(self, wallet: Wallet, amount: Token) -> None:
        """credits the wallet with the specified amount"""
        if amount.value <= 0:
            raise DomainError("Amount must be positive")
        wallet.balance += amount
        
    def debit(self, wallet: Wallet, amount: Token) -> None:
        """debits the wallet with the specified amount"""
        if amount.value <= 0:
            raise DomainError("Amount must be positive")
        if wallet.balance < amount:
            raise DomainError("Insufficient balance in wallet")
        wallet.balance -= amount
    
    def get_balance(self, wallet: Wallet) -> Balance:
        """returns the current balance of the wallet"""
        return wallet.balance
    
    def transfer(self, from_wallet: Wallet, to_wallet: Wallet, amount: Token) -> None:
        """transfers amount from one wallet to another"""
        if from_wallet.id_ == to_wallet.id_:
            raise DomainError("Cannot transfer to the same wallet")
        if amount.value <= 0:
            raise DomainError("Amount must be positive")
        if from_wallet.balance < amount:
            raise DomainError("Insufficient balance in source wallet")
        
        from_wallet.balance -= amount
        to_wallet.balance += amount
