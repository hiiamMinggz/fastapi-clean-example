from app.domain.base import DomainError
from app.domain.challenge.value_objects import ChallengeId

class ChallengeNotFoundByIdError(DomainError):
    def __init__(self, challenge_id: ChallengeId):
        message = f"Challenge with challenge_id {challenge_id.value!r} is not found."
        super().__init__(message)