from abc import abstractmethod
from typing import Protocol

from app.domain.challenge.challenge import Challenge
from app.domain.shared.value_objects.id import ProductId


class ChallengeCommandGateway(Protocol):
    @abstractmethod
    def add(self, challenge: Challenge) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, challenge_id: ProductId) -> Challenge | None:
        """:raises DataMapperError:"""
    