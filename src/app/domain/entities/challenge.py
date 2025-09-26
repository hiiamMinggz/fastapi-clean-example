from app.domain.entities.base import Entity
from app.domain.enums.challenge_status import Status
from app.domain.enums.fee import Fee
from app.domain.value_objects.id import ChallengeId, ViewerId, StreamerId
from app.domain.value_objects.text import Title, Description
from app.domain.value_objects.token import ChallengeAmount, StreamerChallengeFixedAmount
from app.domain.value_objects.time import CreatedAt, ExpiresAt, AcceptedAt
from app.domain.exceptions.base import DomainError

class Challenge(Entity[ChallengeId]):
    def __init__(
        self,
        *,
        id_: ChallengeId,
        title: Title,
        description: Description,
        created_by: ViewerId,
        assigned_to: StreamerId,
        amount: ChallengeAmount,
        fee: Fee,
        streamer_fixed_amount: StreamerChallengeFixedAmount,
        status: Status,
        created_at: CreatedAt,
        expires_at: ExpiresAt,
        accepted_at: AcceptedAt,
    ) -> None:
        super().__init__(id_=id_)
        self.title = title
        self.description = description
        self.created_by = created_by
        self.assigned_to = assigned_to
        self.amount = amount
        self.fee = fee
        self.streamer_fixed_amount = streamer_fixed_amount
        self.status = status
        self.created_at = created_at
        self.expires_at = expires_at
        self.accepted_at = accepted_at
        self.validate()

    def validate(self) -> None:
        self._amount_validation()
        self._time_validation()
        self._creator_validation()

    def _amount_validation(self) -> None:
        if self.amount < self.streamer_fixed_amount:
            raise DomainError(
                f"Challenge amount must be greater than or equal to {self.streamer_fixed_amount}, but got {self.amount}.",
            )

    def _time_validation(self) -> None:
        if self.created_at > self.expires_at:
            raise DomainError(
                f"Challenge created at must be less than or equal to expires at, but got {self.created_at} and {self.expires_at}.",
            )
    def _creator_validation(self) -> None:
        if self.created_by == self.assigned_to:
            raise DomainError(
                f"Challenge creator cannot be the same as assignee",
            )