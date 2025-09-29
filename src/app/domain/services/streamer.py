from app.domain.entities.streamer_profile import Streamer
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.id_generator import IdGenerator
from app.domain.value_objects.credibility import Credibility
from app.domain.value_objects.raw_password import RawPassword
from app.domain.value_objects.id import UserId
from app.domain.value_objects.text import Email
from app.domain.value_objects.time import CreatedAt, UpdatedAt
from app.domain.value_objects.token import Balance, StreamerChallengeFixedAmount
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username import Username

class StreamerService:
    def __init__(
        self,
        user_id_generator: IdGenerator,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher

    def create_streamer(
        self,
        username: Username,
        raw_password: RawPassword,
        email: Email,
        channel_name: str,
        followers_count: int,
        url_stream: str,
        banner_url: str,
        min_amount_challenge: StreamerChallengeFixedAmount,
        created_at: CreatedAt,
        updated_at: UpdatedAt,
    ) -> Streamer:

        id = UserId(self._user_id_generator())
        password_hash = UserPasswordHash(self._password_hasher.hash(raw_password))
        return Streamer(
            id_=id,
            username=username,
            email=email,
            password_hash=password_hash,
            locked=False,
            credibility=Credibility(0),
            balance=Balance(0),
            channel_name=channel_name,
            followers_count=followers_count,
            url_stream=url_stream,
            banner_url=banner_url,
            min_amount_challenge=min_amount_challenge,
            created_at=created_at,
            updated_at=updated_at,
        )

    def is_password_valid(self, streamer: Streamer, raw_password: RawPassword) -> bool:
        return self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=streamer.password_hash.value,
        )

    def change_password(self, streamer: Streamer, raw_password: RawPassword) -> None:
        hashed_password = UserPasswordHash(self._password_hasher.hash(raw_password))
        streamer.password_hash = hashed_password

    def toggle_streamer_activation(self, streamer: Streamer, *, locked: bool) -> None:
        streamer.locked = locked

