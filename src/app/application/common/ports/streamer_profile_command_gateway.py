from abc import abstractmethod
from typing import Protocol

from app.domain.entities.streamer_profile import StreamerProfile
from app.domain.entities.user import User
from app.domain.value_objects.id import UserId
from app.domain.value_objects.username import Username


class StreamerProfileCommandGateway(Protocol):
    @abstractmethod
    def add(self, streamer_profile: StreamerProfile) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, streamer_profile_id: UserId) -> StreamerProfile | None:
        """:raises DataMapperError:"""

