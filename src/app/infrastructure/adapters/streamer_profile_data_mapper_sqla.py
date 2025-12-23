from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.streamer_profile_command_gateway import StreamerProfileCommandGateway
from app.domain.user.streamer_profile import StreamerProfile
from app.domain.user.value_objects import UserId
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError


class SqlaStreamerProfileDataMapper(StreamerProfileCommandGateway):
    def __init__(self, session: MainAsyncSession):
        self._session = session

    def add(self, streamer_profile: StreamerProfile) -> None:
        """:raises DataMapperError:"""
        try:
            self._session.add(streamer_profile)

        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

    async def read_by_id(self, streamer_profile_id: UserId) -> StreamerProfile | None:
        """:raises DataMapperError:"""
        select_stmt: Select[tuple[StreamerProfile]] = select(StreamerProfile).where(StreamerProfile.id_ == streamer_profile_id)  # type: ignore

        try:
            streamer_profile: StreamerProfile | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return streamer_profile

        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error
