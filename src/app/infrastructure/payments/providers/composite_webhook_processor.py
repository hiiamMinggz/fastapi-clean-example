from typing import Mapping

from app.application.common.ports.payment_webhook import (
    PaymentWebhookEvent,
    PaymentWebhookProcessor,
)


class CompositePaymentWebhookProcessor(PaymentWebhookProcessor):
    def __init__(self, processors: dict[str, PaymentWebhookProcessor]):
        self._processors = processors

    async def parse(
        self,
        provider_key: str,
        headers: Mapping[str, str],
        body: bytes,
    ) -> PaymentWebhookEvent:
        processor = self._processors.get(provider_key) or self._processors.get("default")
        if processor is None:
            raise ValueError(f"No webhook processor registered for provider '{provider_key}'.")
        return await processor.parse(provider_key, headers, body)


