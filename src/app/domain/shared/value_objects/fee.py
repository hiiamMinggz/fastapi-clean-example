from dataclasses import dataclass
from typing import ClassVar, Final
from decimal import Decimal

from app.domain.base import DomainFieldError
from app.domain.base import ValueObject



@dataclass(frozen=True, slots=True, repr=False)
class ChallengeFee(ValueObject):
    """raises DomainFieldError"""
    MIN_CHALLENGE_FEE: ClassVar[Final[Decimal]] = Decimal("0.0")
    MAX_CHALLENGE_FEE: ClassVar[Final[Decimal]] = Decimal("1.0")
    DEFAULT_CHALLENGE_FEE: ClassVar[Final[Decimal]] = Decimal("0.2")
    
    value: Decimal


    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_challenge_fee(self.value)


    def _validate_challenge_fee(self, challenge_fee_value: Decimal) -> None:
        """:raises DomainFieldError:"""

        if not isinstance(challenge_fee_value, Decimal):
            raise DomainFieldError(
                f"Challenge fee must be a decimal value.",
            )
        if challenge_fee_value < self.MIN_CHALLENGE_FEE or challenge_fee_value > self.MAX_CHALLENGE_FEE:
            raise DomainFieldError(
                f"Challenge fee must be between "
                f"{self.MIN_CHALLENGE_FEE} and "
                f"{self.MAX_CHALLENGE_FEE}.",
            )
        
@dataclass(frozen=True, slots=True, repr=False)
class DonateFee(ValueObject):
    """raises DomainFieldError"""
    MIN_DONATE_FEE: ClassVar[Final[Decimal]] = Decimal("0.0")
    MAX_DONATE_FEE: ClassVar[Final[Decimal]] = Decimal("1.0")
    DEFAULT_DONATE_FEE: ClassVar[Final[Decimal]] = Decimal("0.1")
    
    value: Decimal


    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(DonateFee, self).__post_init__()
        self._validate_donate_fee(self.value)


    def _validate_donate_fee(self, challenge_fee_value: Decimal) -> None:
        """:raises DomainFieldError:"""

        if not isinstance(challenge_fee_value, Decimal):
            raise DomainFieldError(
                f"Challenge fee must be a decimal value.",
            )
        if challenge_fee_value < self.MIN_DONATE_FEE or challenge_fee_value > self.MAX_DONATE_FEE:
            raise DomainFieldError(
                f"Challenge fee must be between "
                f"{self.MIN_DONATE_FEE} and "
                f"{self.MAX_DONATE_FEE}.",
            )
        
@dataclass(frozen=True, slots=True, repr=False)
class ChallengeFee(ValueObject):
    """raises DomainFieldError"""
    MIN_CHALLENGE_FEE: ClassVar[Final[Decimal]] = Decimal("0.0")
    MAX_CHALLENGE_FEE: ClassVar[Final[Decimal]] = Decimal("1.0")
    DEFAULT_CHALLENGE_FEE: ClassVar[Final[Decimal]] = Decimal("0.2")
    
    value: Decimal


    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_challenge_fee(self.value)


    def _validate_challenge_fee(self, challenge_fee_value: Decimal) -> None:
        """:raises DomainFieldError:"""
        if challenge_fee_value < self.MIN_CHALLENGE_FEE or challenge_fee_value > self.MAX_CHALLENGE_FEE:
            raise DomainFieldError(
                f"Challenge fee must be between "
                f"{self.MIN_CHALLENGE_FEE} and "
                f"{self.MAX_CHALLENGE_FEE}.",
            )
