from abc import abstractmethod
from typing import Protocol

from app.domain.value_objects.id import ViewerId


class AccessRevoker(Protocol):
    @abstractmethod
    async def remove_all_user_access(self, user_id: ViewerId) -> None:
        """:raises DataMapperError:"""
