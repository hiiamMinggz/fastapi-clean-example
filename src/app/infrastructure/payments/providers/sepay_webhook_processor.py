from datetime import datetime
from typing import Mapping

from app.application.common.ports.payment_webhook import (
    PaymentWebhookEvent,
    PaymentWebhookProcessor,
)
from app.domain.enums.payment_status import PaymentStatus
from app.domain.value_objects.id import PaymentId


class SePayWebhookProcessor(PaymentWebhookProcessor):
    async def parse(
        self,
        provider_key: str,
        headers: Mapping[str, str],
        body: bytes,
    ) -> PaymentWebhookEvent:
        # Body is JSON with Vietnamese keys (SePay example)
        import json

        payload = json.loads(body.decode("utf-8")) if body else {}

        # Example fields (see user's sample)
        reference_code = payload.get("referenceCode")
        transfer_type = payload.get("transferType")
        transfer_amount = payload.get("transferAmount")
        transaction_date = payload.get("transactionDate")
        # We don't have our internal payment_id in callback, use external reference

        # Map to status: in => captured, out => refunded
        if transfer_type == "in":
            status = PaymentStatus.CAPTURED
        elif transfer_type == "out":
            status = PaymentStatus.REFUNDED
        else:
            status = PaymentStatus.FAILED

        # SePay does not include our UUID, return None to lookup by external_reference
        return PaymentWebhookEvent(
            provider_key=provider_key,
            payment_id=None,
            external_reference=reference_code,
            status=status,
        )


