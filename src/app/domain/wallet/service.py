from decimal import Decimal
from datetime import datetime, timezone

from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.shared.value_objects.token import Token
from app.domain.shared.value_objects.time import CreatedAt, UpdatedAt
from app.domain.base import DomainError

from app.domain.wallet.wallet import Wallet
from app.domain.wallet.value_objects import WalletId, Balance
from app.domain.user.value_objects import UserId


class WalletService:
    def __init__(self, wallet_id_generator: IdGenerator):
        self._wallet_id_generator = wallet_id_generator
    
    def create_wallet(
        self,
        owner_id: UserId,
    ) -> Wallet:
        """creates a new Wallet instance"""
        wallet_id = WalletId(self._wallet_id_generator())
        now = datetime.now(timezone.utc)

        wallet = Wallet(
            id_=wallet_id,
            owner_id=owner_id,
            balance=Balance(Balance.ZERO),
            created_at=CreatedAt(now),
            updated_at=UpdatedAt(now),
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
    
    @property
    def balance(self, wallet: Wallet) -> Token:
        """returns the balance of the wallet"""
        return wallet.balance

