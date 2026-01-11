from sqlalchemy import UUID, Column, DateTime, Enum, Numeric, String, Table
from sqlalchemy.orm import composite

from app.domain.challenge.challenge import Challenge
from app.domain.challenge.challenge_status import ChallengeStatus

from app.domain.challenge.value_objects import ChallengeAmount, ChallengeId, Description, Title
from app.domain.shared.value_objects.fee import ChallengeFee
from app.domain.shared.value_objects.time import AcceptedAt, CreatedAt, ExpiresAt
from app.domain.user.value_objects import StreamerChallengeFixedAmount, StreamerId, UserId
from app.infrastructure.persistence_sqla.registry import mapping_registry

challenges_table = Table(
    "challenges",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("title", String(Title.MAX_LEN), nullable=False),
    Column("description", String(Description.MAX_LEN), nullable=True),
    Column("created_by", UUID(as_uuid=True), nullable=False),
    Column("assigned_to", UUID(as_uuid=True), nullable=False),
    Column("amount", Numeric(precision=12, scale=2), nullable=False),
    Column("fee", Numeric(precision=12, scale=2), nullable=False),
    Column("streamer_fixed_amount", Numeric(precision=12, scale=2), nullable=False),
    Column(
        "status",
        Enum(ChallengeStatus, name="challengestatus"),
        default=ChallengeStatus.PENDING,
        nullable=False,
    ),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("accepted_at", DateTime(timezone=True), nullable=True),
)


def map_challenges_table() -> None:
    mapping_registry.map_imperatively(
        Challenge,
        challenges_table,
        properties={
            "id_": composite(ChallengeId, challenges_table.c.id),
            "title": composite(Title, challenges_table.c.title),
            "description": composite(Description, challenges_table.c.description),
            "created_by": composite(UserId, challenges_table.c.created_by),
            "assigned_to": composite(StreamerId, challenges_table.c.assigned_to),
            "amount": composite(ChallengeAmount, challenges_table.c.amount),
            "fee": composite(ChallengeFee, challenges_table.c.fee),
            "streamer_fixed_amount": composite(StreamerChallengeFixedAmount, challenges_table.c.streamer_fixed_amount),
            "status": challenges_table.c.status,
            "created_at": composite(CreatedAt, challenges_table.c.created_at),
            "expires_at": composite(ExpiresAt, challenges_table.c.expires_at),
            "accepted_at": composite(AcceptedAt, challenges_table.c.accepted_at),
        },
        column_prefix="_",
    )