from sqlalchemy import UUID, Boolean, Column, DateTime, Numeric, Table
from sqlalchemy.orm import composite

from app.domain.shared.value_objects.time import CreatedAt, UpdatedAt, VerifiedAt
from app.domain.user.streamer import Streamer
from app.domain.user.value_objects import (
    StreamerChallengeFixedAmount,
    StreamerId,
    UserId,
    VerifiedBy,
)
from app.infrastructure.persistence_sqla.registry import mapping_registry

streamers_table = Table(
    "streamers",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("user_id", UUID(as_uuid=True), nullable=False, unique=True),
    Column("is_verified", Boolean, default=False, nullable=False),
    Column("min_amount_challenge", Numeric(precision=12, scale=2), nullable=False),
    Column("disable_challenges", Boolean, default=False, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("verified_at", DateTime(timezone=True), nullable=True),
    Column("verified_by", UUID(as_uuid=True), nullable=True),
)


def map_streamers_table() -> None:
    mapping_registry.map_imperatively(
        Streamer,
        streamers_table,
        properties={
            "id_": composite(StreamerId, streamers_table.c.id),
            "user_id": composite(UserId, streamers_table.c.user_id),
            "is_verified": streamers_table.c.is_verified,
            "min_amount_challenge": composite(
                StreamerChallengeFixedAmount,
                streamers_table.c.min_amount_challenge,
            ),
            "disable_challenges": streamers_table.c.disable_challenges,
            "created_at": composite(CreatedAt, streamers_table.c.created_at),
            "updated_at": composite(UpdatedAt, streamers_table.c.updated_at),
            "verified_at": composite(VerifiedAt, streamers_table.c.verified_at),
            "verified_by": composite(VerifiedBy, streamers_table.c.verified_by),
        },
        column_prefix="_",
    )
