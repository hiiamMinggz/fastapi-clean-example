from enum import StrEnum
from typing import Any

from app.domain.exceptions.challenge import InvalidChallengeStatusError


class Status(StrEnum):
    @classmethod
    def _missing_(cls, value: Any) -> None:
        """Called when a value is not found in the enum"""
        raise InvalidChallengeStatusError(
            f"Invalid challenge status: {value}. "
            f"Valid statuses are: {', '.join(cls.__members__.keys())}"
        )
        
    PENDING = "pending"
    ACCEPTED = "accepted"
    STREAMER_REJECTED = "rejected"
    STREAMER_COMPLETED = "streamer_completed"
    VIEWER_CONFIRMED = "viewer_confirmed"
    VIEWER_REJECTED = "viewer_rejected"
    REFUNDED = "refunded"
    DONE = "done"