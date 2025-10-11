import uuid

import json
from typing import Mapping

from app.application.common.ports.payment_gateway import PaymentProvider
from app.application.common.ports.payment_webhook import (
    PaymentWebhookEvent,
    PaymentWebhookProcessor,
)
from app.domain.enums.payment_status import PaymentStatus
from app.domain.value_objects.id import PaymentId
from app.domain.entities.payment import Payment


class MockPaymentProvider(PaymentProvider):
    async def authorize(self, payment: Payment) -> str | None:
        return f"mock-{uuid.uuid4()}"

    async def capture(self, payment: Payment) -> None:
        return None

    async def refund(self, payment: Payment, amount_minor: int | None = None) -> None:
        return None


class MockPaymentWebhookProcessor(PaymentWebhookProcessor):
    async def parse(
        self,
        provider_key: str,
        headers: Mapping[str, str],
        body: bytes,
    ) -> PaymentWebhookEvent:
        # Expect JSON body: {"payment_id": "uuid", "status": "captured|refunded|failed|authorized", "external_reference": "..."}
        payload = json.loads(body.decode("utf-8")) if body else {}
        payment_id_value = payload.get("payment_id")
        status_raw = payload.get("status", "failed")
        external_reference = payload.get("external_reference")

        try:
            status = PaymentStatus(status_raw)
        except ValueError:
            status = PaymentStatus.FAILED

        payment_id = PaymentId(payment_id_value) if payment_id_value else None
        return PaymentWebhookEvent(
            provider_key=provider_key,
            payment_id=payment_id,
            external_reference=external_reference,
            status=status,
        )


