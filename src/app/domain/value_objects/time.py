from dataclasses import dataclass
from functools import total_ordering
from typing import ClassVar, Final, Optional

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.base import ValueObject
from datetime import datetime

@total_ordering
@dataclass(frozen=True, slots=True, repr=False)
class Time(ValueObject):
    """raises DomainFieldError"""

    value: datetime

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return self.value < other.value

@dataclass(frozen=True, slots=True, repr=False)
class CreatedAt(Time):
    pass

@dataclass(frozen=True, slots=True, repr=False)
class ExpiresAt(Time):
    """raises DomainFieldError"""
    pass

@dataclass(frozen=True, slots=True, repr=False)
class AcceptedAt(Time):
    """raises DomainFieldError"""
    pass
     
@dataclass(frozen=True, slots=True, repr=False)
class UpdatedAt(Time):
    """raises DomainFieldError"""
    pass

@dataclass(frozen=True, slots=True, repr=False)
class DeletedAt(Time):
    """raises DomainFieldError"""
    pass
