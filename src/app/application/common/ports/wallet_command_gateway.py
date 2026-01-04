from abc import abstractmethod
from typing import Protocol

from app.domain.user.value_objects import UserId
from app.domain.wallet.wallet import Wallet
from app.domain.wallet.value_objects import WalletId


class WalletCommandGateway(Protocol):
    @abstractmethod
    def add(self, wallet: Wallet) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, wallet_id: WalletId) -> Wallet | None:
        """:raises DataMapperError:"""
    
    @abstractmethod
    async def read_by_user_id(
        self,
        user_id: UserId,
        for_update: bool = False,
    ) -> Wallet | None:
        """:raises DataMapperError:"""
