from datetime import datetime, timezone
from collections.abc import Mapping
from app.domain.challenge.challenge import Challenge
from app.domain.challenge.challenge_history import ChallengeHistory
from app.domain.challenge.value_objects import (
    Title,
    Description,
    ChallengeAmount,    
)
from app.domain.user.value_objects import StreamerChallengeFixedAmount
from app.domain.shared.value_objects.id import ChallengeHistoryId, ProductId, UserId
from app.domain.challenge.challenge_status import ChallengeStatus
from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.shared.value_objects.time import CreatedAt, ExpiresAt, AcceptedAt, UpdatedAt
from app.domain.shared.value_objects.fee import ChallengeFee
from app.domain.challenge.challenge_status import ChallengeStatus
from app.domain.base import DomainError


class ChallengeService:
    def __init__(
        self,
        challenge_id_generator: IdGenerator,
        history_id_generator: IdGenerator,
    ):
        self.challenge_id_generator = challenge_id_generator
        self.history_id_generator = history_id_generator

    def create_challenge(
            self,
            title: Title,
            description: Description | None,
            created_by: UserId,
            assigned_to: UserId,
            amount: ChallengeAmount,
            streamer_fixed_amount: StreamerChallengeFixedAmount,
            expires_at: ExpiresAt,
            history_collector: list[ChallengeHistory] | None = None,
         ) -> Challenge:
        
        challenge_id = ProductId(self.challenge_id_generator())
        now = datetime.now(timezone.utc)

        challenge = Challenge(
            id_=challenge_id,
            title=title,
            description=description,
            created_by=created_by,
            assigned_to=assigned_to,
            amount=amount,
            fee=ChallengeFee(ChallengeFee.DEFAULT_CHALLENGE_FEE),
            streamer_fixed_amount=streamer_fixed_amount,
            status=ChallengeStatus.PENDING,
            created_at=CreatedAt(now),
            expires_at=expires_at,
            accepted_at=None,
        )
        self._record_history(
            history_collector,
            challenge=challenge,
            previous_status=None,
            current_status=challenge.status,
            changed_by=created_by,
            changed_at=CreatedAt(now),
            changes=ChallengeHistory.build_changes(
                title_from=None,
                title_to=challenge.title.value,
                description_from=None,
                description_to=challenge.description.value,
                amount_from=None,
                amount_to=challenge.amount.value,
                expires_at_from=None,
                expires_at_to=challenge.expires_at.value,
            ),
        )
        return challenge

    def update_challenge_content(
        self,
        challenge: Challenge,
        *,
        title: Title,
        description: Description,
        changed_by: UserId | None = None,
        history_collector: list[ChallengeHistory] | None = None,
    ) -> None:
        if challenge.status == ChallengeStatus.PENDING:
            now = datetime.now(timezone.utc)
            updated_at = UpdatedAt(now)

            previous_title = challenge.title.value
            previous_description = challenge.description.value

            challenge.title = title
            challenge.description = description
            challenge.updated_at = updated_at

            self._record_history(
                history_collector,
                challenge=challenge,
                previous_status=challenge.status,
                current_status=challenge.status,
                changed_by=changed_by,
                changed_at=CreatedAt(now),
                changes=ChallengeHistory.build_changes(
                    title_from=previous_title,
                    title_to=challenge.title.value,
                    description_from=previous_description,
                    description_to=challenge.description.value,
                ),
            )
        else:
            raise DomainError(
                "Challenge contents can only be updated for PENDING challenges"
            )

    def update_challenge_amount(
        self,
        challenge: Challenge,
        *,
        amount: ChallengeAmount,
        changed_by: UserId | None = None,
        history_collector: list[ChallengeHistory] | None = None,
    ) -> None:
        if challenge.status not in {ChallengeStatus.PENDING, ChallengeStatus.STREAMER_ACCEPTED}:
            raise DomainError(
                "Challenge amount can only be updated for PENDING or ACCEPTED challenges"
            )
        if challenge.status == ChallengeStatus.STREAMER_ACCEPTED:
            if amount <= challenge.amount:
                raise DomainError(
                    f"New challenge amount ({amount}) must be greater than current amount ({challenge.amount})"
                )
        now = datetime.now(timezone.utc)
        updated_at = UpdatedAt(now)
        previous_amount = challenge.amount.value

        challenge.amount = amount
        challenge.updated_at = updated_at

        self._record_history(
            history_collector,
            challenge=challenge,
            previous_status=challenge.status,
            current_status=challenge.status,
            changed_by=changed_by,
            changed_at=CreatedAt(now),
            changes=ChallengeHistory.build_changes(
                amount_from=previous_amount,
                amount_to=challenge.amount.value,
            ),
        )
        
    def extend_challenge_deadline(
        self,
        challenge: Challenge,
        *,
        expires_at: ExpiresAt,
        changed_by: UserId | None = None,
        history_collector: list[ChallengeHistory] | None = None,
    ) -> None:
        if challenge.status not in {ChallengeStatus.PENDING, ChallengeStatus.STREAMER_ACCEPTED}:
            raise DomainError(
                "Challenge deadline can only be extended for PENDING or ACCEPTED challenges"
            )
        if expires_at <= challenge.expires_at:
            raise DomainError(
                f"New expiration time ({expires_at}) must be later than current expiration time ({challenge.expires_at})"
            )
        now = datetime.now(timezone.utc)
        updated_at = UpdatedAt(now)
        previous_expires_at = challenge.expires_at.value

        challenge.expires_at = expires_at
        challenge.updated_at = updated_at

        self._record_history(
            history_collector,
            challenge=challenge,
            previous_status=challenge.status,
            current_status=challenge.status,
            changed_by=changed_by,
            changed_at=CreatedAt(now),
            changes=ChallengeHistory.build_changes(
                expires_at_from=previous_expires_at,
                expires_at_to=challenge.expires_at.value,
            ),
        )

    def streamer_accept_challenge(
        self,
        challenge: Challenge,
        *,
        changed_by: UserId | None = None,
        history_collector: list[ChallengeHistory] | None = None,
    ) -> None:
        if challenge.status != ChallengeStatus.PENDING:
            raise DomainError(
                "Challenge can only be ACCEPTED for PENDING challenges"
            )
        if challenge.status == ChallengeStatus.STREAMER_ACCEPTED:
            raise DomainError(
                "Challenge has already been ACCEPTED by the Streamer"
            )
        now = datetime.now(timezone.utc)
        accepted_at = AcceptedAt(now)
        previous_status = challenge.status

        challenge.status = ChallengeStatus.STREAMER_ACCEPTED
        challenge.accepted_at = accepted_at

        self._record_history(
            history_collector,
            challenge=challenge,
            previous_status=previous_status,
            current_status=challenge.status,
            changed_by=changed_by,
            changed_at=CreatedAt(now),
            changes=None,
        )

    def streamer_reject_challenge(
        self,
        challenge: Challenge,
        *,
        changed_by: UserId | None = None,
        history_collector: list[ChallengeHistory] | None = None,
    ) -> None:
        if challenge.status != ChallengeStatus.PENDING:
            raise DomainError(
                "Challenge can only be REJECTED by the Streamer for PENDING challenges"
            )
        if challenge.status == ChallengeStatus.STREAMER_REJECTED:
            raise DomainError(
                "Challenge has already been REJECTED by the Streamer"
            )
        now = datetime.now(timezone.utc)
        updated_at = UpdatedAt(now)
        previous_status = challenge.status

        challenge.status = ChallengeStatus.STREAMER_REJECTED
        challenge.updated_at = updated_at

        self._record_history(
            history_collector,
            challenge=challenge,
            previous_status=previous_status,
            current_status=challenge.status,
            changed_by=changed_by,
            changed_at=CreatedAt(now),
            changes=None,
        )

    def viewer_reject_challenge(
        self,
        challenge: Challenge,
        *,
        changed_by: UserId | None = None,
        history_collector: list[ChallengeHistory] | None = None,
    ) -> None:
        if challenge.status not in {ChallengeStatus.PENDING, ChallengeStatus.STREAMER_ACCEPTED}:
            raise DomainError(
                "Challenge can only be REJECTED by the Viewer for PENDING or ACCEPTED challenges"
            )
        if challenge.status == ChallengeStatus.VIEWER_REJECTED:
            raise DomainError(
                "Challenge has already been REJECTED by the Viewer"
            )
        now = datetime.now(timezone.utc)
        updated_at = UpdatedAt(now)
        previous_status = challenge.status

        challenge.status = ChallengeStatus.VIEWER_REJECTED
        challenge.updated_at = updated_at

        self._record_history(
            history_collector,
            challenge=challenge,
            previous_status=previous_status,
            current_status=challenge.status,
            changed_by=changed_by,
            changed_at=CreatedAt(now),
            changes=None,
        )
        
    def streamer_complete_challenge(
        self,
        challenge: Challenge,
        *,
        changed_by: UserId | None = None,
        history_collector: list[ChallengeHistory] | None = None,
    ) -> None:
        if challenge.status != ChallengeStatus.STREAMER_ACCEPTED:
            raise DomainError(
                "Challenge can only be marked as COMPLETED by the Streamer for ACCEPTED challenges"
            )
        if challenge.status == ChallengeStatus.STREAMER_COMPLETED:
            raise DomainError(
                "Challenge has already been COMPLETED by the Streamer"
            )
        now = datetime.now(timezone.utc)
        
        current_duration = now - challenge.created_at.value
        if current_duration > challenge.duration:
            raise DomainError(
                "Challenge cannot be marked as COMPLETED after its duration has passed"
            )
        previous_status = challenge.status

        updated_at = UpdatedAt(now)
        challenge.status = ChallengeStatus.STREAMER_COMPLETED
        challenge.updated_at = updated_at

        self._record_history(
            history_collector,
            challenge=challenge,
            previous_status=previous_status,
            current_status=challenge.status,
            changed_by=changed_by,
            changed_at=CreatedAt(now),
            changes=None,
        )
        
    def viewer_confirm_challenge(
        self,
        challenge: Challenge,
        *,
        changed_by: UserId | None = None,
        history_collector: list[ChallengeHistory] | None = None,
    ) -> None:
        if challenge.status not in {ChallengeStatus.STREAMER_COMPLETED, ChallengeStatus.STREAMER_ACCEPTED}:
            raise DomainError(
                "Challenge can only be marked as COMPLETED by the Streamer for ACCEPTED or STREAMER_COMPLETED challenges"
            )
        if challenge.status == ChallengeStatus.VIEWER_CONFIRMED:
            raise DomainError(
                "Challenge has already been CONFIRMED by the Viewer"
            )
        now = datetime.now(timezone.utc)
        updated_at = UpdatedAt(now)
        previous_status = challenge.status

        challenge.status = ChallengeStatus.VIEWER_CONFIRMED
        challenge.updated_at = updated_at

        self._record_history(
            history_collector,
            challenge=challenge,
            previous_status=previous_status,
            current_status=challenge.status,
            changed_by=changed_by,
            changed_at=CreatedAt(now),
            changes=None,
        )

    def done_challenge(
        self,
        challenge: Challenge,
        *,
        changed_by: UserId | None = None,
        history_collector: list[ChallengeHistory] | None = None,
    ) -> None:
        if challenge.status != ChallengeStatus.VIEWER_CONFIRMED:
            raise DomainError(
                "Challenge can only be marked as DONE for VIEWER_CONFIRMED challenges"
            )
        now = datetime.now(timezone.utc)
        updated_at = UpdatedAt(now)
        previous_status = challenge.status

        challenge.status = ChallengeStatus.DONE
        challenge.updated_at = updated_at

        self._record_history(
            history_collector,
            challenge=challenge,
            previous_status=previous_status,
            current_status=challenge.status,
            changed_by=changed_by,
            changed_at=CreatedAt(now),
            changes=None,
        )

    def _record_history(
        self,
        history_collector: list[ChallengeHistory] | None,
        *,
        challenge: Challenge,
        previous_status: ChallengeStatus | None,
        current_status: ChallengeStatus,
        changed_by: UserId | None,
        changed_at: CreatedAt,
        changes: Mapping[str, Mapping[str, object]] | None,
    ) -> None:
        if history_collector is None:
            return
        history_collector.append(
            ChallengeHistory(
                id_=self._new_history_id(),
                challenge_id=challenge.id_,
                previous_status=previous_status,
                current_status=current_status,
                changed_by=changed_by,
                changed_at=changed_at,
                changes=changes,
            )
        )

    def _new_history_id(self) -> ChallengeHistoryId:
        return ChallengeHistoryId(self.history_id_generator())
