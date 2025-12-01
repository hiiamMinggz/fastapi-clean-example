from dataclasses import dataclass
from uuid import UUID

from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class UserId(ValueObject):
    value: UUID

class WalletId(ValueObject):
    value: UUID

@dataclass(frozen=True, slots=True, repr=False)
class ChallengeId(ValueObject):
    value: UUID

@dataclass(frozen=True, slots=True, repr=False)
class DonateId(ValueObject):
    value: UUID

@dataclass(frozen=True, slots=True, repr=False)
class CompetitiveId(ValueObject):
    value: UUID
