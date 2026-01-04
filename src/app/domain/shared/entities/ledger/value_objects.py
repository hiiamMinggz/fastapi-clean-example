

from dataclasses import dataclass
from uuid import UUID

from app.domain.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class EntryId(ValueObject):
    """raises DomainFieldError"""
    value: UUID


@dataclass(frozen=True, slots=True, repr=False)
class AccountId(ValueObject):
    """raises DomainFieldError"""
    value: UUID

