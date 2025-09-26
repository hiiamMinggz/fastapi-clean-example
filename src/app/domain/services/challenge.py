from app.domain.entities.challenge import Challenge
from app.domain.value_objects.text import Title, Description
from app.domain.value_objects.token import ChallengeAmount, StreamerChallengeFixedAmount
from app.domain.value_objects.time import CreatedAt, ExpiresAt, AcceptedAt
from app.domain.value_objects.id import ViewerId, StreamerId
from app.domain.enums.fee import Fee
from app.domain.enums.challenge_status import Status
from app.domain.ports.id_generator import IdGenerator


class ChallengeService:
    def __init__(self, challenge_id_generator: IdGenerator):
        self.challenge_id_generator = challenge_id_generator

    def create_challenge(
            self,
            title: Title,
            description: Description,
            created_by: ViewerId,
            assigned_to: StreamerId,
            amount: ChallengeAmount,
            fee: Fee,
            streamer_fixed_amount: StreamerChallengeFixedAmount,
            status: Status,
            created_at: CreatedAt,
            expires_at: ExpiresAt,
            accepted_at: AcceptedAt,
        ) -> Challenge:
        """:raises DataMapperError:"""
        
        challenge_id = self.challenge_id_generator()
        challenge = Challenge(
            id_=challenge_id,
            title=title,
            description=description,
            created_by=created_by,
            assigned_to=assigned_to,
            amount=amount,
            fee=fee,
            streamer_fixed_amount=streamer_fixed_amount,
            status=status,
            created_at=created_at,
            expires_at=expires_at,
            accepted_at=accepted_at,
        )
        return challenge

    def update_challenge(
            self,
            challenge: Challenge,
            title: Title,
            description: Description,
    ):
        ...