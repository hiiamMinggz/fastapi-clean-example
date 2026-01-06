from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

from app.domain.base import DomainFieldError, ValueObject
from datetime import datetime

@total_ordering
@dataclass(frozen=True, slots=True, repr=False)
class Time(ValueObject):
    """raises DomainFieldError"""

    value: datetime

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_time_type(self.value)
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Time):
            return NotImplemented
        return self.value < other.value

    def _validate_time_type(self, time_value: datetime) -> None:
        if not isinstance(time_value, datetime):
            raise DomainFieldError(
                f"Time must be a datetime, but got {type(time_value)}.",
            )

@dataclass(frozen=True, slots=True, repr=False)
class CreatedAt(Time):
    """raises DomainFieldError"""

    value: datetime

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(CreatedAt, self).__post_init__()

@dataclass(frozen=True, slots=True, repr=False)
class ExpiresAt(Time):
    """raises DomainFieldError"""

    value: datetime

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(ExpiresAt, self).__post_init__()

@dataclass(frozen=True, slots=True, repr=False)
class AcceptedAt(Time):
    """raises DomainFieldError"""

    value: datetime

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(AcceptedAt, self).__post_init__()
        
@dataclass(frozen=True, slots=True, repr=False)
class UpdatedAt(Time):
    """raises DomainFieldError"""

    value: datetime

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(UpdatedAt, self).__post_init__()

@dataclass(frozen=True, slots=True, repr=False)
class DeletedAt(Time):
    """raises DomainFieldError"""

    value: datetime

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(DeletedAt, self).__post_init__()