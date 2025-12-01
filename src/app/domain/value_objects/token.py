from dataclasses import dataclass
from functools import total_ordering
from typing import ClassVar, Final

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.base import ValueObject
from decimal import Decimal

ZERO: Final[Decimal] = Decimal("0.00")

@total_ordering
@dataclass(frozen=True, slots=True, repr=False)
class Token(ValueObject):
    """raises DomainFieldError"""
    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        pass
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return self.value == other.value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return self.value < other.value
    
    def __add__(self, other: object):
        if not isinstance(other, Token):
            return NotImplemented
        return self.__class__(self.value + other.value)
    
    def __sub__(self, other: object):
        if not isinstance(other, Token):
            return NotImplemented
        return self.__class__(self.value - other.value)
    
    def __mul__(self, scalar: Decimal):
        if not isinstance(scalar, Decimal):
            return NotImplemented
        return self.__class__(self.value * scalar)
            
@dataclass(frozen=True, slots=True, repr=False)
class Balance(Token):
    """raises DomainFieldError"""
    
    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_balance(self.value)

    def _validate_balance(self, balance_value: Decimal) -> None:
        if balance_value < ZERO:
            raise DomainFieldError(
                f"Balance must be greater than or equal to {ZERO}, but got {balance_value}.",
            )
@dataclass(frozen=True, slots=True, repr=False)
class ChallengeAmount(Token):
    """raises DomainFieldError"""
    

    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_challenge_amount(self.value)

    def _validate_challenge_amount(self, challenge_amount_value: Decimal) -> None:
        if challenge_amount_value < ZERO:
            raise DomainFieldError(
                f"Challenge amount must be greater than or equal to {ZERO}, but got {challenge_amount_value}.",
            )
    
@dataclass(frozen=True, slots=True, repr=False)
class DonateAmount(Token):
    """raises DomainFieldError"""
    

    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_donate_amount(self.value)

    def _validate_donate_amount(self, donate_amount_value: Decimal) -> None:
        if donate_amount_value < ZERO:
            raise DomainFieldError(
                f"Donate amount must be greater than or equal to {ZERO}, but got {donate_amount_value}.",
            )

@dataclass(frozen=True, slots=True, repr=False)
class CompetitiveAmount(Token):
    """raises DomainFieldError"""
    

    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_competitive_amount(self.value)

    def _validate_competitive_amount(self, competitive_amount_value: Decimal) -> None:
        if competitive_amount_value < ZERO:
            raise DomainFieldError(
                f"Competitive amount must be greater than or equal to {ZERO}, but got {competitive_amount_value}.",
            )

@dataclass(frozen=True, slots=True, repr=False)
class StreamerChallengeFixedAmount(Token):
    """raises DomainFieldError"""
    

    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        self._validate_streamer_challenge_fixed_amount(self.value)

    def _validate_streamer_challenge_fixed_amount(self, streamer_challenge_fixed_amount_value: Decimal) -> None:
        if streamer_challenge_fixed_amount_value < ZERO:
            raise DomainFieldError(
                f"Streamer challenge fixed amount must be greater than or equal to {ZERO}, but got {streamer_challenge_fixed_amount_value}.",
            )