from abc import abstractmethod
from typing import Protocol

from app.domain.entities.system_wallet import SystemWallet
from app.domain.value_objects.id import UserId


class WalletCommandGateway(Protocol):
    @abstractmethod
    def add(self, wallet: SystemWallet) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, wallet_id: UserId) -> SystemWallet | None:
        """:raises DataMapperError:"""
