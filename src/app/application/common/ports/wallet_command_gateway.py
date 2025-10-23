from abc import abstractmethod
from typing import Protocol

from app.domain.entities.wallet import Wallet
from app.domain.value_objects.id import UserId


class WalletCommandGateway(Protocol):
    @abstractmethod
    def add(self, wallet: Wallet) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, wallet_id: UserId) -> Wallet | None:
        """:raises DataMapperError:"""


