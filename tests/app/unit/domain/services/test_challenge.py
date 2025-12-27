from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.domain.base import DomainError
from app.domain.challenge.challenge_status import Status
from app.domain.challenge.service import ChallengeService
from app.domain.challenge.value_objects import ChallengeAmount, Description, Title
from app.domain.shared.value_objects.time import CreatedAt, ExpiresAt
from tests.app.unit.factories.challenge import (
    create_challenge,
    create_challenge_amount,
    create_challenge_id,
    create_description,
    create_streamer_fixed_amount,
    create_title,
)
from tests.app.unit.factories.value_objects import create_id


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None) -> datetime:
        return cls.fixed_now


def _patch_datetime(monkeypatch: pytest.MonkeyPatch, fixed_now: datetime) -> None:
    FixedDateTime.fixed_now = fixed_now
    monkeypatch.setattr(
        "app.domain.challenge.service.datetime",
        FixedDateTime,
    )


def test_create_challenge_sets_defaults(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected_id = create_challenge_id()
    fixed_now = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)
    challenge_id_generator.return_value = expected_id.value
    sut = ChallengeService(challenge_id_generator)
    expires_at = ExpiresAt(fixed_now + timedelta(days=2))
    title = create_title("First challenge")
    description = create_description("Do something cool")
    created_by = create_id()
    assigned_to = create_id()
    amount = create_challenge_amount()
    streamer_amount = create_streamer_fixed_amount()

    challenge = sut.create_challenge(
        title=title,
        description=description,
        created_by=created_by,
        assigned_to=assigned_to,
        amount=amount,
        streamer_fixed_amount=streamer_amount,
        expires_at=expires_at,
    )

    assert challenge.id_ == expected_id
    assert challenge.title == title
    assert challenge.description == description
    assert challenge.created_by == created_by
    assert challenge.assigned_to == assigned_to
    assert challenge.amount == amount
    assert challenge.streamer_fixed_amount == streamer_amount
    assert challenge.status is Status.PENDING
    assert challenge.created_at.value == fixed_now
    assert challenge.expires_at == expires_at
    assert challenge.accepted_at is None
    challenge_id_generator.assert_called_once()


def test_update_content_when_pending(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.PENDING)
    fixed_now = datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)
    new_title = Title("New title")
    new_description = Description("Updated description")

    sut.update_challenge_content(
        challenge,
        title=new_title,
        description=new_description,
    )

    assert challenge.title == new_title
    assert challenge.description == new_description
    assert challenge.updated_at.value == fixed_now


def test_update_content_rejects_non_pending(
    challenge_id_generator: MagicMock,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.ACCEPTED)

    with pytest.raises(DomainError):
        sut.update_challenge_content(
            challenge,
            title=Title("Title"),
            description=Description("Description"),
        )


def test_update_amount_for_pending(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(
        status=Status.PENDING,
        amount=create_challenge_amount(ChallengeAmount.ZERO + Decimal("10.00")),
    )
    fixed_now = datetime(2024, 1, 3, 15, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)
    new_amount = create_challenge_amount(Decimal("20.00"))

    sut.update_challenge_amount(challenge, amount=new_amount)

    assert challenge.amount == new_amount
    assert challenge.updated_at.value == fixed_now


def test_update_amount_requires_increase_for_accepted(
    challenge_id_generator: MagicMock,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(
        status=Status.ACCEPTED,
        amount=create_challenge_amount(Decimal("30.00")),
    )
    same_amount = create_challenge_amount(Decimal("30.00"))

    with pytest.raises(DomainError):
        sut.update_challenge_amount(challenge, amount=same_amount)


def test_update_amount_rejects_disallowed_status(
    challenge_id_generator: MagicMock,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.DONE)
    new_amount = create_challenge_amount(Decimal("50.00"))

    with pytest.raises(DomainError):
        sut.update_challenge_amount(challenge, amount=new_amount)


def test_extend_deadline_updates_when_later(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.PENDING)
    new_expiration = ExpiresAt(challenge.expires_at.value + timedelta(days=1))
    fixed_now = datetime(2024, 1, 4, 8, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)

    sut.extend_challenge_deadline(challenge, expires_at=new_expiration)

    assert challenge.expires_at == new_expiration
    assert challenge.updated_at.value == fixed_now


def test_extend_deadline_rejects_earlier_or_equal(
    challenge_id_generator: MagicMock,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.ACCEPTED)

    with pytest.raises(DomainError):
        sut.extend_challenge_deadline(challenge, expires_at=challenge.expires_at)


def test_accept_challenge_sets_status_and_timestamp(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.PENDING, accepted_at=None)
    fixed_now = datetime(2024, 1, 5, 12, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)

    sut.accept_challenge(challenge)

    assert challenge.status is Status.ACCEPTED
    assert challenge.accepted_at.value == fixed_now


def test_accept_challenge_rejects_non_pending(
    challenge_id_generator: MagicMock,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.ACCEPTED)

    with pytest.raises(DomainError):
        sut.accept_challenge(challenge)


def test_streamer_rejects_pending_challenge(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.PENDING)
    fixed_now = datetime(2024, 1, 6, 10, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)

    sut.streamer_reject_challenge(challenge)

    assert challenge.status is Status.STREAMER_REJECTED
    assert challenge.updated_at.value == fixed_now


def test_viewer_rejects_pending_or_accepted(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.ACCEPTED)
    fixed_now = datetime(2024, 1, 7, 11, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)

    sut.viewer_reject_challenge(challenge)

    assert challenge.status is Status.VIEWER_REJECTED
    assert challenge.updated_at.value == fixed_now


def test_streamer_complete_challenge_within_duration(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    expires_at = created_at + timedelta(days=1)
    challenge = create_challenge(
        status=Status.ACCEPTED,
        created_at=CreatedAt(created_at),
        expires_at=ExpiresAt(expires_at),
    )
    fixed_now = created_at + timedelta(hours=12)
    _patch_datetime(monkeypatch, fixed_now)

    sut.streamer_complete_challenge(challenge)

    assert challenge.status is Status.STREAMER_COMPLETED
    assert challenge.updated_at.value == fixed_now


def test_streamer_complete_challenge_after_duration_fails(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    expires_at = created_at + timedelta(hours=1)
    challenge = create_challenge(
        status=Status.ACCEPTED,
        created_at=CreatedAt(created_at),
        expires_at=ExpiresAt(expires_at),
    )
    fixed_now = expires_at + timedelta(minutes=1)
    _patch_datetime(monkeypatch, fixed_now)

    with pytest.raises(DomainError):
        sut.streamer_complete_challenge(challenge)


def test_viewer_confirm_after_streamer_completion(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.STREAMER_COMPLETED)
    fixed_now = datetime(2024, 1, 8, 14, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)

    sut.viewer_confirm_challenge(challenge)

    assert challenge.status is Status.VIEWER_CONFIRMED
    assert challenge.updated_at.value == fixed_now


def test_viewer_confirm_invalid_status_raises(
    challenge_id_generator: MagicMock,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.PENDING)

    with pytest.raises(DomainError):
        sut.viewer_confirm_challenge(challenge)


def test_done_challenge_transitions_to_done(
    challenge_id_generator: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.VIEWER_CONFIRMED)
    fixed_now = datetime(2024, 1, 9, 16, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)

    sut.done_challenge(challenge)

    assert challenge.status is Status.DONE
    assert challenge.updated_at.value == fixed_now


def test_done_challenge_requires_viewer_confirmed(
    challenge_id_generator: MagicMock,
) -> None:
    sut = ChallengeService(challenge_id_generator)
    challenge = create_challenge(status=Status.ACCEPTED)

    with pytest.raises(DomainError):
        sut.done_challenge(challenge)
