import logging
from dataclasses import dataclass

from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.challenge_command_gateway import ChallengeCommandGateway
from app.application.common.services.authorization.authorize import (
    authorize,
)
from app.application.common.services.authorization.permissions import (
    CanChangeChallengeStatus,
    ChallengeManagementContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.challenge import Challenge
from app.domain.exceptions.base import DomainError
from app.domain.exceptions.challenge import ChallengeNotFoundByIdError
from app.domain.services.challenge import ChallengeService
from app.domain.value_objects.id import ChallengeId
from app.domain.enums.challenge_status import Status
from uuid import UUID

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ToggleChallengeStatusRequest:
    challenge_id: UUID
    status: Status


class ToggleChallengeStatusInteractor:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        challenge_command_gateway: ChallengeCommandGateway,
        challenge_service: ChallengeService,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._challenge_command_gateway = challenge_command_gateway
        self._challenge_service = challenge_service
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: ToggleChallengeStatusRequest) -> None:
        """
        :raises AuthenticationError: If the current user is not authenticated
        :raises DataMapperError: If there's an error accessing the database
        :raises AuthorizationError: If the user is not authorized to update this challenge
        :raises DomainError: If the challenge is not found or cannot be updated
        :raises DomainFieldError: If the title or description is invalid
        """
        log.info(
            "Toggle challenge status: started. Challenge ID: %s",
            request_data.challenge_id,
        )

        current_user = await self._current_user_service.get_current_user()
        
        challenge_id = ChallengeId(request_data.challenge_id)
        new_status = request_data.status
        
        challenge: Challenge | None = await self._challenge_command_gateway.read_by_id(challenge_id)
        if challenge is None:
            raise ChallengeNotFoundByIdError()

        # Authorize: can only update challenges created by the current user
        authorize(
            CanChangeChallengeStatus(),
            context=ChallengeManagementContext(
                subject=current_user,
                challenge=challenge,
            ),
        )

        if new_status == Status.ACCEPTED:
            self._challenge_service.accept_challenge(
                challenge=challenge
            )
        elif new_status == Status.STREAMER_REJECTED:
            self._challenge_service.streamer_reject_challenge(
                challenge=challenge,
            )
        elif new_status == Status.VIEWER_REJECTED:
            self._challenge_service.viewer_reject_challenge(
                challenge=challenge,
            )
        elif new_status == Status.STREAMER_COMPLETED:
            self._challenge_service.streamer_complete_challenge(
                challenge=challenge,
            )
        elif new_status == Status.VIEWER_CONFIRMED:
            self._challenge_service.viewer_confirm_challenge(
                challenge=challenge,
            )

        await self._challenge_command_gateway.update_by_id(challenge_id, challenge)
        await self._transaction_manager.commit()

        log.info(
            "Toggle challenge status: done. Challenge ID: %s",
            challenge_id,
        )
