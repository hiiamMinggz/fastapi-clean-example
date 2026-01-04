from abc import abstractmethod
from typing import Protocol

from app.domain.ledger.ledger_entry import LedgerEntry
from app.domain.ledger.value_objects import EntryId


class LedgerCommandGateway(Protocol):
    @abstractmethod
    def add(self, ledger_entry: LedgerEntry) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, ledger_entry_id: EntryId) -> EntryId | None:
        """:raises DataMapperError:"""
    
