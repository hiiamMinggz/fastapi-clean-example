from datetime import datetime, timezone
from app.domain.challenge.challenge import Challenge
from app.domain.challenge.value_objects import (
    ChallengeId,
    Title,
    Description,
    ChallengeAmount,    
)
from app.domain.user.value_objects import (
    UserId,
    StreamerChallengeFixedAmount,
)
from app.domain.challenge.challenge_status import ChallengeStatus
from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.shared.value_objects.time import CreatedAt, ExpiresAt, AcceptedAt, UpdatedAt
from app.domain.shared.value_objects.fee import ChallengeFee
from app.domain.challenge.challenge_status import ChallengeStatus
from app.domain.base import DomainError


class ChallengeService:
    def __init__(self, challenge_id_generator: IdGenerator):
        self.challenge_id_generator = challenge_id_generator

    def create_challenge(
            self,
            title: Title,
            description: Description | None,
            created_by: UserId,
            assigned_to: UserId,
            amount: ChallengeAmount,
            streamer_fixed_amount: StreamerChallengeFixedAmount,
            expires_at: ExpiresAt,
         ) -> Challenge:
        
        challenge_id = ChallengeId(self.challenge_id_generator())
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
        return challenge

    def update_challenge_content(
        self,
        challenge: Challenge,
        *,
        title: Title,
        description: Description,
    ) -> None:
        if challenge.status == ChallengeStatus.PENDING:
            now = datetime.now(timezone.utc)
            updated_at = UpdatedAt(now)
            
            challenge.title = title
            challenge.description = description
            challenge.updated_at = updated_at
        else:
            raise DomainError(
                "Challenge contents can only be updated for PENDING challenges"
            )

    def update_challenge_amount(
        self,
        challenge: Challenge,
        *,
        amount: ChallengeAmount,
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
        
        challenge.amount = amount
        challenge.updated_at = updated_at
        
    def extend_challenge_deadline(
        self,
        challenge: Challenge,
        *,
        expires_at: ExpiresAt,
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
        
        challenge.expires_at = expires_at
        challenge.updated_at = updated_at

    def streamer_accept_challenge(self, challenge: Challenge) -> None:
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
        
        challenge.status = ChallengeStatus.STREAMER_ACCEPTED
        challenge.accepted_at = accepted_at

    def streamer_reject_challenge(self, challenge: Challenge) -> None:
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
        
        challenge.status = ChallengeStatus.STREAMER_REJECTED
        challenge.updated_at = updated_at

    def viewer_reject_challenge(self, challenge: Challenge) -> None:
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
            
        challenge.status = ChallengeStatus.VIEWER_REJECTED
        challenge.updated_at = updated_at
        
    def streamer_complete_challenge(self, challenge: Challenge) -> None:
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
            
        updated_at = UpdatedAt(now)
        challenge.status = ChallengeStatus.STREAMER_COMPLETED
        challenge.updated_at = updated_at
        
    def viewer_confirm_challenge(self, challenge: Challenge) -> None:
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
        
        challenge.status = ChallengeStatus.VIEWER_CONFIRMED
        challenge.updated_at = updated_at

    def done_challenge(self, challenge: Challenge) -> None:
        if challenge.status != ChallengeStatus.VIEWER_CONFIRMED:
            raise DomainError(
                "Challenge can only be marked as DONE for VIEWER_CONFIRMED challenges"
            )
        now = datetime.now(timezone.utc)
        updated_at = UpdatedAt(now)
        
        challenge.status = ChallengeStatus.DONE
        challenge.updated_at = updated_at