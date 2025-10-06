from sqlalchemy import UUID, Boolean, Column, Integer, String, Table, DateTime, NUMERIC
from sqlalchemy.orm import composite

from app.domain.entities.streamer_profile import StreamerProfile
from app.domain.value_objects.id import UserId
from app.domain.value_objects.username import Username
from app.domain.value_objects.token import StreamerChallengeFixedAmount
from app.domain.value_objects.time import CreatedAt, UpdatedAt
from app.infrastructure.persistence_sqla.registry import mapping_registry

streamer_profiles_table = Table(
    "streamer_profiles",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("channel_name", String(Username.MAX_LEN), nullable=False, unique=True),
    Column("followers_count", Integer, nullable=False, default=0),
    Column("url_stream", String(1024), nullable=False),
    Column("banner_url", String(1024), nullable=True),
    Column("min_amount_challenge", NUMERIC(12, 2), nullable=False),
    Column("disable_challenges", Boolean, nullable=False, default=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def map_streamer_profiles_table() -> None:
    mapping_registry.map_imperatively(
        StreamerProfile,
        streamer_profiles_table,
        properties={
            "id_": composite(UserId, streamer_profiles_table.c.id),
            "channel_name": streamer_profiles_table.c.channel_name,
            "followers_count": streamer_profiles_table.c.followers_count,
            "url_stream": streamer_profiles_table.c.url_stream,
            "banner_url": streamer_profiles_table.c.banner_url,
            "min_amount_challenge": composite(
                StreamerChallengeFixedAmount,
                streamer_profiles_table.c.min_amount_challenge
            ),
            "disable_challenges": streamer_profiles_table.c.disable_challenges,
            "created_at": composite(CreatedAt, streamer_profiles_table.c.created_at),
            "updated_at": composite(UpdatedAt, streamer_profiles_table.c.updated_at),
        },
        column_prefix="_",
    )
