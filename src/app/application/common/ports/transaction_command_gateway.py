from abc import abstractmethod
from typing import Protocol

from app.domain.shared.entities.transaction.transaction import Transaction
from app.domain.shared.entities.transaction.value_objects import TransactionId


class TransactionCommandGateway(Protocol):
    @abstractmethod
    def add(self, transaction: Transaction) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, transaction_id: TransactionId) -> Transaction | None:
        """:raises DataMapperError:"""
    
