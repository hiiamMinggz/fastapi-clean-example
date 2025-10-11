from app.domain.entities.base import Entity
from app.domain.enums.payment_status import PaymentStatus
from app.domain.value_objects.id import PaymentId, UserId
from app.domain.value_objects.text import Title, Description
from app.domain.value_objects.token import PaymentAmount
from app.domain.value_objects.time import CreatedAt, UpdatedAt


class Payment(Entity[PaymentId]):
    def __init__(
        self,
        *,
        id_: PaymentId,
        payer_id: UserId,
        payee_id: UserId,
        amount: PaymentAmount,
        currency: str,
        description: Description | None,
        status: PaymentStatus,
        external_reference: str | None,
        created_at: CreatedAt,
        updated_at: UpdatedAt,
    ) -> None:
        super().__init__(id_=id_)
        self.payer_id = payer_id
        self.payee_id = payee_id
        self.amount = amount
        self.currency = currency
        self.description = description
        self.status = status
        self.external_reference = external_reference
        self.created_at = created_at
        self.updated_at = updated_at

