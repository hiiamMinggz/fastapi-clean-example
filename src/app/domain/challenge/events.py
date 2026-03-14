from dataclasses import dataclass
from app.domain.base import Event
from app.domain.challenge.value_objects import ChallengeAmount, Description, Title
from app.domain.shared.value_objects.id import ProductId, UserId
from app.domain.shared.value_objects.time import CreatedAt


@dataclass(frozen=True, slots=True, repr=False)
class ChallengeCreated(Event):
    id_: ProductId
    title: Title
    description: Description
    created_by: UserId
    assigned_to: UserId
    amount: ChallengeAmount
    created_at: CreatedAt

@dataclass(frozen=True, slots=True, repr=False)
class ChallengeAcceptedByStreamer(Event):
    id_: ProductId

@dataclass(frozen=True, slots=True, repr=False)
class ChallengeRejectedByStreamer(Event):
    id_: ProductId

@dataclass(frozen=True, slots=True, repr=False)
class ChallengeCompletedByStreamer(Event):
    id_: ProductId

@dataclass(frozen=True, slots=True, repr=False)
class ChallengeConfirmedByViewer(Event):
    id_: ProductId

@dataclass(frozen=True, slots=True, repr=False)
class ChallengeRejectedByViewer(Event):
    id_: ProductId
