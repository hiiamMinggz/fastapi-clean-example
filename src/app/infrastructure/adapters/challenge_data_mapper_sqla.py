from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.challenge_command_gateway import ChallengeCommandGateway
from app.domain.entities.challenge import Challenge
from app.domain.value_objects.id import ChallengeId
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError


class SqlaChallengeDataMapper(ChallengeCommandGateway):
    def __init__(self, session: MainAsyncSession):
        self._session = session

    def add(self, challenge: Challenge) -> None:
        """:raises DataMapperError:"""
        try:
            self._session.add(challenge)
        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

    async def read_by_id(self, challenge_id: ChallengeId) -> Challenge | None:
        """:raises DataMapperError:"""
        select_stmt: Select[tuple[Challenge]] = select(Challenge).where(
            Challenge.id_ == challenge_id  # type: ignore
        )

        try:
            challenge: Challenge | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return challenge

        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

    async def update_by_id(
        self, 
        challenge_id: ChallengeId,
        challenge: Challenge,
    ) -> None:
        """:raises DataMapperError:"""
        try:
            await self._session.merge(challenge)
        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error

    async def delete_by_id(self, challenge_id: ChallengeId) -> None:
        """:raises DataMapperError:"""
        try:
            challenge = await self.read_by_id(challenge_id)
            if challenge is not None:
                await self._session.delete(challenge)
        except SQLAlchemyError as error:
            raise DataMapperError(DB_QUERY_FAILED) from error