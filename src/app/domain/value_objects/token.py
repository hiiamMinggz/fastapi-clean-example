from dataclasses import dataclass
from typing import ClassVar, Final

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.base import ValueObject
from decimal import Decimal

@dataclass(frozen=True, slots=True, repr=False)
class Token(ValueObject):
    """raises DomainFieldError"""
    
    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(Token, self).__post_init__()
        self._validate_token_type(self.value)

    def _validate_token_type(self, token_value: Decimal) -> None:
        if not isinstance(token_value, Decimal):
            raise DomainFieldError(
                f"Token must be a Decimal, but got {type(token_value)}.",
            )
        
@dataclass(frozen=True, slots=True, repr=False)
class Balance(Token):
    """raises DomainFieldError"""
    ZERO: ClassVar[Final[Decimal]] = "0.00"

    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(Balance, self).__post_init__()

    def _validate_balance(self, balance_value: Decimal) -> None:
        if balance_value < self.ZERO:
            raise DomainFieldError(
                f"Balance must be greater than or equal to {self.ZERO}, but got {balance_value}.",
            )
    
@dataclass(frozen=True, slots=True, repr=False)
class ChallengeAmount(Token):
    """raises DomainFieldError"""
    ZERO: ClassVar[Final[Decimal]] = "0.00"

    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(ChallengeAmount, self).__post_init__()
        self._validate_challenge_amount(self.value)

    def _validate_challenge_amount(self, challenge_amount_value: Decimal) -> None:
        if challenge_amount_value < self.ZERO:
            raise DomainFieldError(
                f"Challenge amount must be greater than or equal to {self.ZERO}, but got {challenge_amount_value}.",
            )
    
@dataclass(frozen=True, slots=True, repr=False)
class DonateAmount(Token):
    """raises DomainFieldError"""
    ZERO: ClassVar[Final[Decimal]] = "0.00"

    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(DonateAmount, self).__post_init__()
        self._validate_donate_amount(self.value)

    def _validate_donate_amount(self, donate_amount_value: Decimal) -> None:
        if donate_amount_value < self.ZERO:
            raise DomainFieldError(
                f"Donate amount must be greater than or equal to {self.ZERO}, but got {donate_amount_value}.",
            )

@dataclass(frozen=True, slots=True, repr=False)
class CompetitiveAmount(Token):
    """raises DomainFieldError"""
    ZERO: ClassVar[Final[Decimal]] = "0.00"

    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(CompetitiveAmount, self).__post_init__()
        self._validate_competitive_amount(self.value)

    def _validate_competitive_amount(self, competitive_amount_value: Decimal) -> None:
        if competitive_amount_value < self.ZERO:
            raise DomainFieldError(
                f"Competitive amount must be greater than or equal to {self.ZERO}, but got {competitive_amount_value}.",
            )

@dataclass(frozen=True, slots=True, repr=False)
class StreamerChallengeFixedAmount(Token):
    """raises DomainFieldError"""
    ZERO: ClassVar[Final[Decimal]] = "0.00"

    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(StreamerChallengeFixedAmount, self).__post_init__()
        self._validate_streamer_challenge_fixed_amount(self.value)

    def _validate_streamer_challenge_fixed_amount(self, streamer_challenge_fixed_amount_value: Decimal) -> None:
        if streamer_challenge_fixed_amount_value < self.ZERO:
            raise DomainFieldError(
                f"Streamer challenge fixed amount must be greater than or equal to {self.ZERO}, but got {streamer_challenge_fixed_amount_value}.",
            )