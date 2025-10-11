from dataclasses import dataclass
from typing import Mapping, Protocol

from app.domain.enums.payment_status import PaymentStatus
from app.domain.value_objects.id import PaymentId


@dataclass(frozen=True, slots=True)
class PaymentWebhookEvent:
    provider_key: str
    payment_id: PaymentId | None
    external_reference: str | None
    status: PaymentStatus


class PaymentWebhookProcessor(Protocol):
    async def parse(
        self,
        provider_key: str,
        headers: Mapping[str, str],
        body: bytes,
    ) -> PaymentWebhookEvent:
        ...


