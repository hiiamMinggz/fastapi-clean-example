from abc import abstractmethod
from typing import Protocol

from app.domain.entities.challenge import Challenge
from app.domain.value_objects.id import ChallengeId


class ChallengeCommandGateway(Protocol):
    @abstractmethod
    def add(self, challenge: Challenge) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, challenge_id: ChallengeId) -> Challenge | None:
        """:raises DataMapperError:"""
    
    @abstractmethod
    async def update_by_id(self, challenge_id: ChallengeId, challenge: Challenge) -> None:
        """:raises DataMapperError:"""
    
    @abstractmethod
    async def delete_by_id(self, challenge_id: ChallengeId) -> None:
        """:raises DataMapperError:"""

