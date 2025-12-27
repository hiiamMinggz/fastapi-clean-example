from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID
import uuid6

from app.domain.challenge.challenge import Challenge
from app.domain.challenge.challenge_status import Status
from app.domain.challenge.value_objects import (
    ChallengeAmount,
    ChallengeId,
    Description,
    Title,
)
from app.domain.shared.value_objects.fee import ChallengeFee
from app.domain.shared.value_objects.time import AcceptedAt, CreatedAt, ExpiresAt
from app.domain.user.value_objects import (
    StreamerChallengeFixedAmount,
    UserId,
)
from tests.app.unit.factories.value_objects import create_id


def create_challenge_id(value: UUID | None = None) -> ChallengeId:
    return ChallengeId(value or uuid6.uuid7())


def create_title(value: str = "Challenge Title") -> Title:
    return Title(value)


def create_description(value: str = "Complete the task") -> Description:
    return Description(value)


def create_challenge_amount(value: Decimal = Decimal("100.00")) -> ChallengeAmount:
    return ChallengeAmount(value)


def create_streamer_fixed_amount(
    value: Decimal = Decimal("10.00"),
) -> StreamerChallengeFixedAmount:
    return StreamerChallengeFixedAmount(value)


def create_created_at(value: datetime | None = None) -> CreatedAt:
    return CreatedAt(value or datetime.now(timezone.utc))


def create_expires_at(value: datetime | None = None) -> ExpiresAt:
    base = value or datetime.now(timezone.utc) + timedelta(days=1)
    return ExpiresAt(base)


def create_accepted_at(value: datetime | None = None) -> AcceptedAt:
    return AcceptedAt(value or datetime.now(timezone.utc))


def create_challenge(
    *,
    challenge_id: ChallengeId | None = None,
    title: Title | None = None,
    description: Description | None = None,
    created_by: UserId | None = None,
    assigned_to: UserId | None = None,
    amount: ChallengeAmount | None = None,
    fee: ChallengeFee | None = None,
    streamer_fixed_amount: StreamerChallengeFixedAmount | None = None,
    status: Status = Status.PENDING,
    created_at: CreatedAt | None = None,
    expires_at: ExpiresAt | None = None,
    accepted_at: AcceptedAt | None = None,
) -> Challenge:
    created_by_vo = created_by or create_id()
    assigned_to_vo = assigned_to or create_id()
    created_at_vo = created_at or create_created_at()
    expires_at_vo = expires_at or ExpiresAt(created_at_vo.value + timedelta(days=1))
    return Challenge(
        id_=challenge_id or create_challenge_id(),
        title=title or create_title(),
        description=description or create_description(),
        created_by=created_by_vo,
        assigned_to=assigned_to_vo,
        amount=amount or create_challenge_amount(),
        fee=fee or ChallengeFee(ChallengeFee.DEFAULT_CHALLENGE_FEE),
        streamer_fixed_amount=streamer_fixed_amount or create_streamer_fixed_amount(),
        status=status,
        created_at=created_at_vo,
        expires_at=expires_at_vo,
        accepted_at=accepted_at,
    )
