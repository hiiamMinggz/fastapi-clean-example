from sqlalchemy import UUID, Column, DateTime, Enum, Numeric, String, Table
from sqlalchemy.orm import composite

from app.domain.entities.payment import Payment
from app.domain.enums.payment_status import PaymentStatus
from app.domain.value_objects.id import PaymentId, UserId
from app.domain.value_objects.text import Description
from app.domain.value_objects.token import PaymentAmount
from app.domain.value_objects.time import CreatedAt, UpdatedAt
from app.infrastructure.persistence_sqla.registry import mapping_registry


payments_table = Table(
    "payments",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("payer_id", UUID(as_uuid=True), nullable=False),
    Column("payee_id", UUID(as_uuid=True), nullable=False),
    Column("amount", Numeric(precision=12, scale=2), nullable=False),
    Column("currency", String(3), nullable=False),
    Column("description", String(Description.MAX_LEN), nullable=True),
    Column("status", Enum(PaymentStatus, name="paymentstatus"), nullable=False),
    Column("external_reference", String(255), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def map_payments_table() -> None:
    mapping_registry.map_imperatively(
        Payment,
        payments_table,
        properties={
            "id_": composite(PaymentId, payments_table.c.id),
            "payer_id": composite(UserId, payments_table.c.payer_id),
            "payee_id": composite(UserId, payments_table.c.payee_id),
            "amount": composite(PaymentAmount, payments_table.c.amount),
            "currency": payments_table.c.currency,
            "description": composite(Description, payments_table.c.description),
            "status": payments_table.c.status,
            "external_reference": payments_table.c.external_reference,
            "created_at": composite(CreatedAt, payments_table.c.created_at),
            "updated_at": composite(UpdatedAt, payments_table.c.updated_at),
        },
        column_prefix="_",
    )


