from abc import abstractmethod
from typing import Protocol

from app.domain.value_objects.id import ViewerId


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> ViewerId:
        """:raises AuthenticationError:"""
