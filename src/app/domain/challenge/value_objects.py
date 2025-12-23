from dataclasses import dataclass
from typing import ClassVar, Final, Optional
from uuid import UUID
from app.domain.base import DomainFieldError, ValueObject
from app.domain.shared.value_objects.token import Token
from decimal import Decimal

@dataclass(frozen=True, slots=True, repr=False)
class ChallengeId(ValueObject):
    value: UUID
    

@dataclass(frozen=True, slots=True, repr=False)
class Title(ValueObject):
    """raises DomainFieldError"""

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 255

    value: str

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_title_length(self.value)

    def _validate_title_length(self, title_value: str) -> None:
        """:raises DomainFieldError:"""
        if len(title_value) < self.MIN_LEN or len(title_value) > self.MAX_LEN:
            raise DomainFieldError(
                f"Title must be between "
                f"{self.MIN_LEN} and "
                f"{self.MAX_LEN} characters.",
            )
        

@dataclass(frozen=True, slots=True, repr=False)
class Description(ValueObject):
    """raises DomainFieldError"""

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 255

    value: str

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_description_length(self.value)

    def _validate_description_length(self, description_value: str) -> None:
        """:raises DomainFieldError:"""
        if len(description_value) < self.MIN_LEN or len(description_value) > self.MAX_LEN:
            raise DomainFieldError(
                f"Description must be between "
                f"{self.MIN_LEN} and "
                f"{self.MAX_LEN} characters.",
            )
            
@dataclass(frozen=True, slots=True, repr=False)
class ChallengeAmount(Token):
    """raises DomainFieldError"""
    ZERO: ClassVar[Final[Decimal]] = Decimal("0.00")

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(ChallengeAmount, self).__post_init__()
        self._validate_challenge_amount(self.value)

    def _validate_challenge_amount(self, challenge_amount_value: Decimal) -> None:
        if challenge_amount_value < self.ZERO:
            raise DomainFieldError(
                f"Challenge amount must be greater than or equal to {self.ZERO}, but got {challenge_amount_value}.",
            )