from app.domain.base import Entity
from app.domain.shared.value_objects.time import CreatedAt, UpdatedAt, VerifiedAt
from app.domain.user.streamer_profile import StreamerProfile
from app.domain.user.value_objects import StreamerId, UserId, VerifiedBy

class Streamer(Entity[StreamerId]):
    def __init__(
        self,
        *,
        id_: StreamerId,
        user_id: UserId,
        profile: StreamerProfile,
        is_verified: bool,
        created_at: CreatedAt,
        updated_at: UpdatedAt,
        verified_at: VerifiedAt,
        verified_by: VerifiedBy,
    ) -> None:
        super().__init__(id_=id_)
        self.user_id = user_id
        self.profile = profile
        self.is_verified = is_verified
        self.created_at = created_at
        self.updated_at = updated_at
        self.verified_at = verified_at
        self.verified_by = verified_by
    
    #TODO: add validation for verified_by (only system admins can verify)
        