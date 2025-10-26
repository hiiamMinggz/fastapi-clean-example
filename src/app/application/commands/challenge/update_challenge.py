from datetime import datetime, timezone
from decimal import Decimal
import logging
from dataclasses import dataclass

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.challenge_command_gateway import ChallengeCommandGateway
from app.application.common.services.authorization.authorize import (
    authorize,
)
from app.application.common.services.authorization.composite import AnyOf
from app.application.common.services.authorization.permissions import (
    CanExtendChallengeDeadline,
    CanUpdateChallengeAmount,
    CanUpdateChallengeContent,
    ChallengeManagementContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.challenge import Challenge
from app.domain.exceptions.base import DomainError
from app.domain.exceptions.challenge import ChallengeNotFoundByIdError
from app.domain.services.challenge import ChallengeService
from app.domain.value_objects.text import Title, Description
from app.domain.value_objects.id import ChallengeId
from typing import Optional
from uuid import UUID

from app.domain.value_objects.time import ExpiresAt, UpdatedAt
from app.domain.value_objects.token import ChallengeAmount

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateChallengeRequest:
    challenge_id: UUID
    title: Optional[str]
    description: Optional[str]
    amount: Optional[Decimal]
    expires_at: Optional[datetime]

class UpdateChallengeInteractor:
    def __init__(
        self,
        current_user_service: CurrentUserService,
        challenge_command_gateway: ChallengeCommandGateway,
        challenge_service: ChallengeService,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._challenge_command_gateway = challenge_command_gateway
        self._challenge_service = challenge_service
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: UpdateChallengeRequest) -> None:
        """
        :raises AuthenticationError: If the current user is not authenticated
        :raises DataMapperError: If there's an error accessing the database
        :raises AuthorizationError: If the user is not authorized to update this challenge
        :raises DomainError: If the challenge is not found or cannot be updated
        :raises DomainFieldError: If the title or description is invalid
        """
        log.info(
            "Update challenge: started. Challenge ID: %s",
            request_data.challenge_id,
        )
        challenge_id = ChallengeId(request_data.challenge_id)
        current_user = await self._current_user_service.get_current_user()
        challenge: Challenge | None = await self._challenge_command_gateway.read_by_id(challenge_id)
        if challenge is None:
            raise ChallengeNotFoundByIdError()
        
        if request_data.title is not None:
            authorize(
                CanUpdateChallengeContent(),
                context=ChallengeManagementContext(
                    subject=current_user,
                    challenge=challenge,
                ),
            )
            new_title = Title(request_data.title)
            new_description = Description(request_data.description)
            
            self._challenge_service.update_challenge_content(
                challenge=challenge,
                title=new_title,
                description=new_description,
            )
        if request_data.amount is not None:
            authorize(
                CanUpdateChallengeAmount(),
                context=ChallengeManagementContext(
                    subject=current_user,
                    challenge=challenge,
                ),
            )
            new_amount = ChallengeAmount(request_data.amount)
            self._challenge_service.update_challenge_amount(
                challenge=challenge,
                amount=new_amount,
            )
        if request_data.expires_at is not None:
            authorize(
                CanExtendChallengeDeadline(),
                context=ChallengeManagementContext(
                    subject=current_user,
                    challenge=challenge,
                ),
            )
            new_expires_at = ExpiresAt(request_data.expires_at)
            self._challenge_service.extend_challenge_deadline(
                challenge=challenge,
                expires_at=new_expires_at,
            )
        
        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "Update challenge: done. Challenge ID: %s",
            challenge_id,
        )
