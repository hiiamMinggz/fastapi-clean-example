from sqlalchemy import UUID, Column, DateTime, Enum, Numeric, String, Table
from sqlalchemy.orm import composite

from app.domain.entities.challenge import Challenge
from app.domain.enums.challenge_status import Status
from app.domain.enums.fee import Fee
from app.domain.value_objects.id import ChallengeId, UserId
from app.domain.value_objects.text import Title, Description
from app.domain.value_objects.token import ChallengeAmount, StreamerChallengeFixedAmount
from app.domain.value_objects.time import CreatedAt, ExpiresAt, AcceptedAt
from app.infrastructure.persistence_sqla.registry import mapping_registry

challenges_table = Table(
    "challenges",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("title", String(Title.MAX_LEN), nullable=False),
    Column("description", String(Description.MAX_LEN), nullable=True),
    Column("created_by", UUID(as_uuid=True), nullable=False),
    Column("assigned_to", UUID(as_uuid=True), nullable=False),
    Column("amount", Numeric(precision=10, scale=2), nullable=False),
    Column("fee", Enum(Fee, name="challengefee"), nullable=False),
    Column("streamer_fixed_amount", Numeric(precision=10, scale=2), nullable=False),
    Column(
        "status",
        Enum(Status, name="challengestatus"),
        default=Status.PENDING,
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
            "assigned_to": composite(UserId, challenges_table.c.assigned_to),
            "amount": composite(ChallengeAmount, challenges_table.c.amount),
            "fee": challenges_table.c.fee,
            "streamer_fixed_amount": composite(StreamerChallengeFixedAmount, challenges_table.c.streamer_fixed_amount),
            "status": challenges_table.c.status,
            "created_at": composite(CreatedAt, challenges_table.c.created_at),
            "expires_at": composite(ExpiresAt, challenges_table.c.expires_at),
            "accepted_at": composite(AcceptedAt, challenges_table.c.accepted_at),
        },
        column_prefix="_",
    )