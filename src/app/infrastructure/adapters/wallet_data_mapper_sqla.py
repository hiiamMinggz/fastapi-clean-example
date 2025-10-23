from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.wallet_command_gateway import WalletCommandGateway
from app.domain.entities.wallet import Wallet
from app.domain.value_objects.id import UserId
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError


class SqlaWalletDataMapper(WalletCommandGateway):
    def __init__(self, session: MainAsyncSession):
        self._session = session

    def add(self, wallet: Wallet) -> None:
        """:raises DataMapperError:"""
        try:
            self._session.add(wallet)

        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

    async def read_by_id(self, wallet_id: UserId) -> Wallet | None:
        """:raises DataMapperError:"""
        select_stmt: Select[tuple[Wallet]] = select(Wallet).where(Wallet.id_ == wallet_id)  # type: ignore

        try:
            wallet: Wallet | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return wallet

        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

