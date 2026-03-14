from abc import abstractmethod
from typing import Protocol

from app.domain.shared.value_objects.id import UserId, WalletId
from app.domain.wallet.wallet import Wallet


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
