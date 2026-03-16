from abc import abstractmethod
from typing import Protocol

from app.domain.shared.value_objects.id import StreamerId, UserId
from app.domain.user.streamer import Streamer

class StreamerCommandGateway(Protocol):
    @abstractmethod
    def add(self, streamer: Streamer) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, streamer_id: StreamerId, for_update: bool = False) -> Streamer | None:
        """:raises DataMapperError:"""
    
    @abstractmethod
    async def read_by_user_id(self, user_id: UserId, for_update: bool = False) -> Streamer | None:
        """:raises DataMapperError:"""

