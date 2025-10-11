from abc import abstractmethod
from typing import Protocol

from app.domain.entities.payment import Payment
from app.domain.value_objects.id import PaymentId


class PaymentCommandGateway(Protocol):
    @abstractmethod
    def add(self, payment: Payment) -> None:
        ":raises DataMapperError:"

    @abstractmethod
    async def read_by_id(self, payment_id: PaymentId) -> Payment | None:
        ":raises DataMapperError:"

    @abstractmethod
    async def update_by_id(self, payment_id: PaymentId, payment: Payment) -> None:
        ":raises DataMapperError:"

    @abstractmethod
    async def read_by_external_reference(self, external_reference: str) -> Payment | None:
        ":raises DataMapperError:"


class PaymentProvider(Protocol):
    @abstractmethod
    async def authorize(self, payment: Payment) -> str | None:
        """
        Returns provider-specific external reference or None.
        """

    @abstractmethod
    async def capture(self, payment: Payment) -> None:
        ...

    @abstractmethod
    async def refund(self, payment: Payment, amount_minor: int | None = None) -> None:
        ...

