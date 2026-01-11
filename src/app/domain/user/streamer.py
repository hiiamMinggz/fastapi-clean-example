from app.domain.base import Entity
from app.domain.shared.value_objects.time import CreatedAt, UpdatedAt, VerifiedAt
from app.domain.user.value_objects import StreamerChallengeFixedAmount, StreamerId, UserId, VerifiedBy

class Streamer(Entity[StreamerId]):
    def __init__(
        self,
        *,
        id_: StreamerId,
        user_id: UserId,
        is_verified: bool,
        min_amount_challenge: StreamerChallengeFixedAmount,
        disable_challenges: bool,
        created_at: CreatedAt,
        updated_at: UpdatedAt,
        verified_at: VerifiedAt,
        verified_by: VerifiedBy,
    ) -> None:
        super().__init__(id_=id_)
        self.user_id = user_id
        self.is_verified = is_verified
        self.min_amount_challenge = min_amount_challenge
        self.disable_challenges = disable_challenges
        self.created_at = created_at
        self.updated_at = updated_at
        self.verified_at = verified_at
        self.verified_by = verified_by
    
    #TODO: add validation for verified_by (only system admins can verify)
        