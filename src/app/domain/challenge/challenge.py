from datetime import timedelta
from app.domain.base import Entity, DomainError
from app.domain.shared.value_objects.id import ProductId
from app.domain.shared.value_objects.time import AcceptanceDeadline, CreatedAt, ExecutionTime, ExpiresAt, AcceptedAt
from app.domain.shared.value_objects.id import UserId, StreamerId
from app.domain.challenge.value_objects import (
    Title,
    Description,
    ChallengeAmount,
)
from app.domain.shared.value_objects.fee import ChallengeFee
from app.domain.challenge.challenge_status import ChallengeStatus
from app.domain.user.value_objects import StreamerChallengeFixedAmount


class Challenge(Entity[ProductId]):
    def __init__(
        self,
        *,
        id_: ProductId,
        title: Title,
        description: Description,
        created_by: UserId,
        assigned_to: StreamerId,
        amount: ChallengeAmount,
        fee: ChallengeFee,
        streamer_fixed_amount: StreamerChallengeFixedAmount,
        status: ChallengeStatus,
        created_at: CreatedAt,
        acceptance_deadline: AcceptanceDeadline,
        execution_time: ExecutionTime,
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
        self.acceptance_deadline = acceptance_deadline
        self.execution_time = execution_time
        self.expires_at = expires_at
        self.accepted_at = accepted_at
        self.validate()

    def validate(self) -> None:
        self._amount_validation()
        self._time_validation()

    def _amount_validation(self) -> None:
        if self.amount < self.streamer_fixed_amount:
            raise DomainError(
                f"Challenge amount must be greater than or equal to {self.streamer_fixed_amount}, but got {self.amount}.",
            )

    def _time_validation(self) -> None:
        if self.acceptance_deadline <= self.created_at:
            raise DomainError(
                f"Challenge acceptance deadline must be greater than created at, but got {self.acceptance_deadline} and {self.created_at}.",
            )
    
    @property
    def duration(self) -> timedelta:
        return self.expires_at.value - self.accepted_at.value