from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.transaction_command_gateway import (
    TransactionCommandGateway,
)
from app.domain.shared.entities.transaction.transaction import Transaction
from app.domain.shared.entities.transaction.value_objects import TransactionId
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError


class SqlaTransactionDataMapper(TransactionCommandGateway):
    def __init__(self, session: MainAsyncSession):
        self._session = session

    def add(self, transaction: Transaction) -> None:
        """:raises DataMapperError:"""
        try:
            self._session.add(transaction)

        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

    async def read_by_id(self, transaction_id: TransactionId) -> Transaction | None:
        """:raises DataMapperError:"""
        select_stmt: Select[tuple[Transaction]] = select(Transaction).where(Transaction.id_ == transaction_id)  # type: ignore
        try:
            transaction: Transaction | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

        return transaction
