from app.domain.entities.challenge import Challenge
from app.domain.value_objects.text import Title, Description
from app.domain.value_objects.token import ChallengeAmount, StreamerChallengeFixedAmount
from app.domain.value_objects.time import CreatedAt, ExpiresAt, AcceptedAt, UpdatedAt
from app.domain.value_objects.id import UserId, ChallengeId
from app.domain.enums.fee import Fee
from app.domain.enums.challenge_status import Status
from app.domain.ports.id_generator import IdGenerator
from app.domain.exceptions.base import DomainError


class ChallengeService:
    def __init__(self, challenge_id_generator: IdGenerator):
        self.challenge_id_generator = challenge_id_generator

    def create_challenge(
            self,
            title: Title,
            description: Description,
            created_by: UserId,
            assigned_to: UserId,
            amount: ChallengeAmount,
            fee: Fee,
            streamer_fixed_amount: StreamerChallengeFixedAmount,
            status: Status,
            created_at: CreatedAt,
            expires_at: ExpiresAt,
         ) -> Challenge:
        
        challenge_id = ChallengeId(self.challenge_id_generator())
        challenge = Challenge(
            id_=challenge_id,
            title=title,
            description=description,
            created_by=created_by,
            assigned_to=assigned_to,
            amount=amount,
            fee=fee,
            streamer_fixed_amount=streamer_fixed_amount,
            status=status,
            created_at=created_at,
            expires_at=expires_at,
        )
        return challenge

    def update_challenge_content(
        self,
        challenge: Challenge,
        *,
        title: Title,
        description: Description,
        updated_at: UpdatedAt,
    ) -> None:
        if challenge.status == Status.PENDING:
            challenge.title = title
            challenge.description = description
            challenge.updated_at = updated_at
        else:
            raise DomainError(
                "Challenge title can only be updated for PENDING challenges"
            )

    def update_challenge_amount(
        self,
        challenge: Challenge,
        *,
        amount: ChallengeAmount,
        updated_at: UpdatedAt,
    ) -> None:
        if challenge.status not in {Status.PENDING, Status.ACCEPTED}:
            raise DomainError(
                "Challenge amount can only be updated for PENDING or ACCEPTED challenges"
            )
        if challenge.status == Status.ACCEPTED:
            if amount <= challenge.amount:
                raise DomainError(
                    f"New challenge amount ({amount}) must be greater than current amount ({challenge.amount})"
                )
        challenge.amount = amount
        challenge.updated_at = updated_at
        
    def extend_challenge_deadline(
        self,
        challenge: Challenge,
        *,
        expires_at: ExpiresAt,
        updated_at: UpdatedAt,
    ) -> None:
        if challenge.status not in {Status.PENDING, Status.ACCEPTED}:
            raise DomainError(
                "Challenge deadline can only be extended for PENDING or ACCEPTED challenges"
            )
        if expires_at <= challenge.expires_at:
            raise DomainError(
                f"New expiration time ({expires_at}) must be later than current expiration time ({challenge.expires_at})"
            )
        challenge.expires_at = expires_at
        challenge.updated_at = updated_at

    def accept_challenge(self, challenge: Challenge, accepted_at: AcceptedAt) -> None:
        if challenge.status != Status.PENDING:
            raise DomainError(
                "Challenge can only be ACCEPTED for PENDING challenges"
            )
        challenge.status = Status.ACCEPTED
        challenge.accepted_at = accepted_at

    def streamer_reject_challenge(self, challenge: Challenge, updated_at: UpdatedAt) -> None:
        if challenge.status != Status.PENDING:
            raise DomainError(
                "Challenge can only be REJECTED by the Streamer for PENDING challenges"
            )
        challenge.status = Status.STREAMER_REJECTED
        challenge.updated_at = updated_at
    def viewer_reject_challenge(self, challenge: Challenge, updated_at: UpdatedAt) -> None:
        if challenge.status not in {Status.PENDING, Status.ACCEPTED}:
            raise DomainError(
                "Challenge can only be REJECTED by the Viewer for PENDING or ACCEPTED challenges"
            )
        challenge.status = Status.VIEWER_REJECTED
        challenge.updated_at = updated_at
        
    def streamer_complete_challenge(self, challenge: Challenge, updated_at: UpdatedAt) -> None:
        if challenge.status != Status.ACCEPTED:
            raise DomainError(
                "Challenge can only be marked as COMPLETED by the Streamer for ACCEPTED challenges"
            )
        challenge.status = Status.STREAMER_COMPLETED
        challenge.updated_at = updated_at
        
    def viewer_confirm_challenge(self, challenge: Challenge, updated_at: UpdatedAt) -> None:
        if challenge.status not in {Status.STREAMER_COMPLETED, Status.ACCEPTED}:
            raise DomainError(
                "Challenge can only be marked as COMPLETED by the Streamer for ACCEPTED or STREAMER_COMPLETED challenges"
            )
        challenge.status = Status.VIEWER_CONFIRMED
        challenge.updated_at = updated_at

    def done_challenge(self, challenge: Challenge, updated_at: UpdatedAt) -> None:
        if challenge.status != Status.VIEWER_CONFIRMED:
            raise DomainError(
                "Challenge can only be marked as DONE for VIEWER_CONFIRMED challenges"
            )
        challenge.status = Status.DONE
        challenge.updated_at = updated_at