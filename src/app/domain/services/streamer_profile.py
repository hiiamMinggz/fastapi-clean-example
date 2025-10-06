from datetime import datetime, timezone

from app.domain.entities.streamer_profile import StreamerProfile
from app.domain.entities.user import User
from app.domain.value_objects.raw_password import RawPassword
from app.domain.value_objects.id import UserId
from app.domain.value_objects.time import CreatedAt, UpdatedAt
from app.domain.value_objects.token import StreamerChallengeFixedAmount
from app.domain.value_objects.user_password_hash import UserPasswordHash


class StreamerProfileService:
    def __init__(self) -> None:
        pass
    
    def create_streamer_profile(
        self,
        streamer_id: UserId,
        channel_name: str,
        followers_count: int,
        url_stream: str,
        banner_url: str,
        min_amount_challenge: StreamerChallengeFixedAmount,
        disable_challenges: bool,
    ) -> StreamerProfile:

        now = datetime.now(timezone.utc)
        created_at = CreatedAt(now)
        updated_at = UpdatedAt(now)
        
        return StreamerProfile(
            id_=streamer_id,
            channel_name=channel_name,
            followers_count=followers_count,
            url_stream=url_stream,
            banner_url=banner_url,
            min_amount_challenge=min_amount_challenge,
            disable_challenges=disable_challenges,
            created_at=created_at,
            updated_at=updated_at,
        )

    def is_password_valid(self, streamer: User, raw_password: RawPassword) -> bool:
        return self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=streamer.password_hash.value,
        )

    def change_password(self, streamer: User, raw_password: RawPassword) -> None:
        hashed_password = UserPasswordHash(self._password_hasher.hash(raw_password))
        streamer.password_hash = hashed_password

    def toggle_streamer_activation(self, streamer: User, *, locked: bool) -> None:
        streamer.locked = locked

