from abc import abstractmethod
from typing import Protocol

from app.domain.user.streamer_profile import StreamerProfile
from app.domain.user.value_objects import UserId


class StreamerProfileCommandGateway(Protocol):
    @abstractmethod
    def add(self, streamer_profile: StreamerProfile) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, streamer_profile_id: UserId) -> StreamerProfile | None:
        """:raises DataMapperError:"""

