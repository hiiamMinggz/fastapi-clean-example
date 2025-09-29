from app.domain.exceptions.base import DomainError
from app.domain.value_objects.id import ChallengeId

class InvalidChallengeStatusError(DomainError):
    """Raised when an invalid challenge status is provided"""
    pass

class ChallengeNotFoundByIdError(DomainError):
    def __init__(self, challenge_id: ChallengeId):
        message = f"Challenge with id {challenge_id.value!r} is not found."
        super().__init__(message)
