from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.streamer_command_gateway import StreamerCommandGateway
from app.domain.user.streamer import Streamer
from app.domain.user.value_objects import StreamerId
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError


class SqlaStreamerDataMapper(StreamerCommandGateway):
    def __init__(self, session: MainAsyncSession):
        self._session = session

    def add(self, streamer: Streamer) -> None:
        """:raises DataMapperError:"""
        try:
            self._session.add(streamer)

        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

    async def read_by_id(self, streamer_id: StreamerId, for_update: bool = False) -> Streamer | None:
        """:raises DataMapperError:"""
        select_stmt: Select[tuple[Streamer]] = select(Streamer).where(Streamer.id_ == streamer_id)  # type: ignore

        if for_update:
            select_stmt = select_stmt.with_for_update()
        try:
            streamer: Streamer | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return streamer
        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error


