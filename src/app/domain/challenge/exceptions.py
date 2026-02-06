from app.domain.base import DomainError
from app.domain.shared.value_objects.id import ProductId

class ChallengeNotFoundByIdError(DomainError):
    def __init__(self, challenge_id: ProductId):
        message = f"Challenge with challenge_id {challenge_id.value!r} is not found."
        super().__init__(message)