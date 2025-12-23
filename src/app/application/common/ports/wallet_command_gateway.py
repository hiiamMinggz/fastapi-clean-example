from abc import abstractmethod
from typing import Protocol

from app.domain.wallet.wallet import Wallet
from app.domain.wallet.value_objects import WalletId


class WalletCommandGateway(Protocol):
    @abstractmethod
    def add(self, wallet: Wallet) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, wallet_id: WalletId) -> Wallet | None:
        """:raises DataMapperError:"""
