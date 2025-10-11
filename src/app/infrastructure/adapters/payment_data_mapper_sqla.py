from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.payment_gateway import PaymentCommandGateway
from app.domain.entities.payment import Payment
from app.domain.value_objects.id import PaymentId
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError


class SqlaPaymentDataMapper(PaymentCommandGateway):
    def __init__(self, session: MainAsyncSession):
        self._session = session

    def add(self, payment: Payment) -> None:
        ":raises DataMapperError:"
        try:
            self._session.add(payment)
        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

    async def read_by_id(self, payment_id: PaymentId) -> Payment | None:
        ":raises DataMapperError:"
        select_stmt: Select[tuple[Payment]] = select(Payment).where(Payment.id_ == payment_id)  # type: ignore

        try:
            payment: Payment | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return payment
        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

    async def update_by_id(self, payment_id: PaymentId, payment: Payment) -> None:
        ":raises DataMapperError:"
        try:
            # Rely on SQLAlchemy unit-of-work tracking; flush will persist changes
            pass
        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

    async def read_by_external_reference(self, external_reference: str) -> Payment | None:
        ":raises DataMapperError:"
        select_stmt: Select[tuple[Payment]] = select(Payment).where(Payment.external_reference == external_reference)  # type: ignore

        try:
            payment: Payment | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return payment
        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error


