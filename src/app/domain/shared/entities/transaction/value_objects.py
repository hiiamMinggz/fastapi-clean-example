from app.domain.base import ValueObject
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, repr=False)
class TransactionId(ValueObject):
    value: UUID

@dataclass(frozen=True, slots=True, repr=False)
class ReferenceId(ValueObject):
    value: UUID