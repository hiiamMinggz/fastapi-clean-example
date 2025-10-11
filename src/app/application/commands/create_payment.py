import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID
from decimal import Decimal

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.payment_gateway import (
    PaymentCommandGateway,
    PaymentProvider,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.payment import Payment
from app.domain.enums.payment_status import PaymentStatus
from app.domain.services.user import UserService
from app.domain.value_objects.id import PaymentId, UserId
from app.domain.value_objects.text import Description
from app.domain.value_objects.time import CreatedAt, UpdatedAt
from app.domain.value_objects.token import PaymentAmount

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatePaymentRequest:
    payer_id: UUID
    payee_id: UUID
    amount: Decimal
    currency: str
    description: str | None


class CreatePaymentResponse(TypedDict):
    id: UUID
    status: PaymentStatus
    external_reference: str | None


class CreatePaymentInteractor:

    def __init__(
        self,
        current_user_service: CurrentUserService,
        payment_gateway: PaymentCommandGateway,
        payment_provider: PaymentProvider,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._payment_gateway = payment_gateway
        self._payment_provider = payment_provider
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: CreatePaymentRequest) -> CreatePaymentResponse:
        log.info(
            "Create payment: started. Payer: '%s', Payee: '%s', Amount: %s %s",
            request_data.payer_id,
            request_data.payee_id,
            request_data.amount,
            request_data.currency,
        )

        # Create VOs
        payment = Payment(
            id_=PaymentId(request_data.payer_id),
            payer_id=UserId(request_data.payer_id),
            payee_id=UserId(request_data.payee_id),
            amount=PaymentAmount(request_data.amount),
            currency=request_data.currency,
            description=Description(request_data.description) if request_data.description else None,
            status=PaymentStatus.INITIATED,
            external_reference=None,
            created_at=CreatedAt.now(),
            updated_at=UpdatedAt.now(),
        )

        self._payment_gateway.add(payment)

        await self._flusher.flush()

        # Authorize with provider
        external_ref = await self._payment_provider.authorize(payment)
        payment.external_reference = external_ref
        payment.status = PaymentStatus.AUTHORIZED
        await self._payment_gateway.update_by_id(payment.id_, payment)

        await self._transaction_manager.commit()

        log.info(
            "Create payment: done. PaymentId: '%s', Status: %s",
            payment.id_.value,
            payment.status,
        )
        return CreatePaymentResponse(
            id=payment.id_.value,
            status=payment.status,
            external_reference=external_ref,
        )


