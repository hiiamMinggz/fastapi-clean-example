from dataclasses import dataclass
from typing import ClassVar, Final

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.base import ValueObject



@dataclass(frozen=True, slots=True, repr=False)
class Credibility(ValueObject):
    """raises DomainFieldError"""
    MIN_CREDIBILITY: ClassVar[Final[float]] = 0.0
    MAX_CREDIBILITY: ClassVar[Final[float]] = 5.0
    
    value: float

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_credibility(self.value)

    def _validate_credibility(self, credibility_value: float) -> None:
        """:raises DomainFieldError:"""
        if credibility_value < self.MIN_CREDIBILITY or credibility_value > self.MAX_CREDIBILITY:
            raise DomainFieldError(
                f"Credibility must be between "
                f"{self.MIN_CREDIBILITY} and "
                f"{self.MAX_CREDIBILITY}.",
            )