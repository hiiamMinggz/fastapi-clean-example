import logging
from dataclasses import dataclass

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.payment_gateway import PaymentCommandGateway
from app.application.common.ports.payment_webhook import (
    PaymentWebhookEvent,
    PaymentWebhookProcessor,
)
from app.application.common.ports.transaction_manager import TransactionManager
from app.domain.enums.payment_status import PaymentStatus
from app.domain.value_objects.id import PaymentId

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProcessPaymentWebhookRequest:
    provider_key: str
    headers: dict[str, str]
    body: bytes


class ProcessPaymentWebhookInteractor:
    def __init__(
        self,
        payment_gateway: PaymentCommandGateway,
        webhook_processor: PaymentWebhookProcessor,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._payment_gateway = payment_gateway
        self._webhook_processor = webhook_processor
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: ProcessPaymentWebhookRequest) -> None:
        event: PaymentWebhookEvent = await self._webhook_processor.parse(
            request.provider_key,
            request.headers,
            request.body,
        )

        payment = None
        if event.payment_id is not None:
            payment = await self._payment_gateway.read_by_id(event.payment_id)
        elif event.external_reference:
            payment = await self._payment_gateway.read_by_external_reference(event.external_reference)
        else:
            log.warning("Webhook event missing both payment_id and external_reference. Provider=%s", event.provider_key)
            return
        if payment is None:
            log.warning(
                "Payment not found for webhook. Provider=%s, PaymentId=%s",
                event.provider_key,
                event.payment_id,
            )
            return

        payment.status = event.status

        await self._payment_gateway.update_by_id(PaymentId(payment.id_.value), payment)
        await self._flusher.flush()
        await self._transaction_manager.commit()


