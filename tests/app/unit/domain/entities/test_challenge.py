from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.domain.base import DomainError
from app.domain.challenge.challenge import Challenge
from app.domain.challenge.challenge_status import Status
from app.domain.challenge.value_objects import ChallengeAmount, Description, Title
from app.domain.shared.value_objects.fee import ChallengeFee
from app.domain.shared.value_objects.time import CreatedAt, ExpiresAt
from app.domain.user.value_objects import StreamerChallengeFixedAmount
from tests.app.unit.factories.challenge import (
    create_challenge,
    create_challenge_amount,
    create_challenge_id,
    create_streamer_fixed_amount,
    create_title,
    create_created_at,
    create_expires_at,
)
from tests.app.unit.factories.value_objects import create_id


def test_challenge_initialization_sets_fields_and_validates() -> None:
    created_at = CreatedAt(datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc))
    expires_at = ExpiresAt(created_at.value + timedelta(days=2))
    amount = create_challenge_amount(Decimal("150.00"))
    streamer_amount = create_streamer_fixed_amount(Decimal("50.00"))
    challenge_id = create_challenge_id()
    title = create_title("Speed run")

    challenge = Challenge(
        id_=challenge_id,
        title=title,
        description=Description("Finish in time"),
        created_by=create_id(),
        assigned_to=create_id(),
        amount=amount,
        fee=ChallengeFee(ChallengeFee.DEFAULT_CHALLENGE_FEE),
        streamer_fixed_amount=streamer_amount,
        status=Status.PENDING,
        created_at=created_at,
        expires_at=expires_at,
        accepted_at=None,
    )

    assert challenge.id_ == challenge_id
    assert challenge.title == title
    assert challenge.amount == amount
    assert challenge.streamer_fixed_amount == streamer_amount
    assert challenge.status is Status.PENDING
    assert challenge.duration == timedelta(days=2)

def test_challenge_initialization_with_empty_description() -> None:
    challenge_id = create_challenge_id()
    title = create_title("Speed run")
    description = None
    created_at = create_created_at()
    eexpires_at = create_expires_at(created_at.value + timedelta(days=1))

    challenge = Challenge(
        id_=challenge_id,
        title=title,
        description=description,
        created_by=create_id(),
        assigned_to=create_id(),
        amount=create_challenge_amount(),
        fee=ChallengeFee(ChallengeFee.DEFAULT_CHALLENGE_FEE),
        streamer_fixed_amount=create_streamer_fixed_amount(),
        status=Status.PENDING,
        created_at=created_at,
        expires_at=eexpires_at,
        accepted_at=None,
    )

    assert challenge.id_ == challenge_id
    assert challenge.title == title
    assert challenge.amount == create_challenge_amount()
    assert challenge.streamer_fixed_amount == create_streamer_fixed_amount()
    assert challenge.status is Status.PENDING
    assert challenge.duration == timedelta(days=1)

def test_raises_when_amount_less_than_streamer_fixed_amount() -> None:
    amount = create_challenge_amount(Decimal("25.00"))
    streamer_amount = create_streamer_fixed_amount(Decimal("50.00"))

    with pytest.raises(DomainError):
        create_challenge(amount=amount, streamer_fixed_amount=streamer_amount)


def test_raises_when_created_after_expiration() -> None:
    created_at = CreatedAt(datetime(2024, 1, 2, tzinfo=timezone.utc))
    expires_at = ExpiresAt(datetime(2024, 1, 1, tzinfo=timezone.utc))

    with pytest.raises(DomainError):
        create_challenge(created_at=created_at, expires_at=expires_at)


def test_raises_when_creator_and_assignee_match() -> None:
    user_id = create_id()

    with pytest.raises(DomainError):
        create_challenge(created_by=user_id, assigned_to=user_id)

def test_raises_when_assignee_and_creator_match() -> None:
    user_id = create_id()

    with pytest.raises(DomainError):
        create_challenge(assigned_to=user_id, created_by=user_id)


def test_duration_computes_difference_between_dates() -> None:
    created_at = CreatedAt(datetime(2024, 1, 1, tzinfo=timezone.utc))
    expires_at = ExpiresAt(created_at.value + timedelta(hours=6))
    challenge = create_challenge(created_at=created_at, expires_at=expires_at)

    assert challenge.duration == timedelta(hours=6)
