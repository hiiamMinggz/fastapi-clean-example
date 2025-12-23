from abc import abstractmethod
from typing import Protocol

from app.domain.challenge.challenge import Challenge
from app.domain.challenge.value_objects import ChallengeId


class ChallengeCommandGateway(Protocol):
    @abstractmethod
    def add(self, challenge: Challenge) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(self, challenge_id: ChallengeId) -> Challenge | None:
        """:raises DataMapperError:"""
    