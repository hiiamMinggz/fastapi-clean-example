from app.domain.entities.base import Entity
from app.domain.enums.user_role import UserRole
from app.domain.value_objects.id import UserId
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username import Username
from app.domain.value_objects.text import Email
from app.domain.value_objects.credibility import Credibility
from app.domain.value_objects.token import StreamerChallengeFixedAmount, Balance
from app.domain.value_objects.time import CreatedAt, UpdatedAt

class Streamer(Entity[UserId]):
    def __init__(
        self,
        *,
        id_: UserId,
        channel_name: str,
        followers_count: int,
        url_stream: str,
        banner_url: str,
        min_amount_challenge: StreamerChallengeFixedAmount,
        disable_challenges: bool,
        created_at: CreatedAt,
        updated_at: UpdatedAt,
    ) -> None:
        super().__init__(id_=id_)
        self.channel_name = channel_name
        self.followers_count = followers_count
        self.url_stream = url_stream
        self.banner_url = banner_url
        self.min_amount_challenge = min_amount_challenge
        self.disable_challenges = disable_challenges
        self.created_at = created_at
        self.updated_at = updated_at

