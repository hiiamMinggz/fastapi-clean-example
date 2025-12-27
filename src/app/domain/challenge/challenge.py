from datetime import timedelta
from app.domain.base import Entity, DomainError
from app.domain.shared.value_objects.time import CreatedAt, ExpiresAt, AcceptedAt
from app.domain.user.value_objects import UserId, StreamerChallengeFixedAmount
from app.domain.challenge.value_objects import (
    ChallengeId,
    Title,
    Description,
    ChallengeAmount,
)
from app.domain.shared.value_objects.fee import ChallengeFee
from app.domain.challenge.challenge_status import Status


class Challenge(Entity[ChallengeId]):
    def __init__(
        self,
        *,
        id_: ChallengeId,
        title: Title,
        description: Description | None,
        created_by: UserId,
        assigned_to: UserId,
        amount: ChallengeAmount,
        fee: ChallengeFee,
        streamer_fixed_amount: StreamerChallengeFixedAmount,
        status: Status,
        created_at: CreatedAt,
        expires_at: ExpiresAt,
        accepted_at: AcceptedAt | None,
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
    
    def _accepted_validation(self) -> None:
        if self.accepted_at is not None and self.accepted_at.value > self.expires_at.value:
            raise DomainError(
                f"Challenge accepted at must be less than or equal to expires at, but got {self.accepted_at} and {self.expires_at}.",
            )
    
    @property
    def duration(self) -> timedelta:
        return self.expires_at.value - self.created_at.value