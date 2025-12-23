from dataclasses import dataclass
from decimal import Decimal
from functools import total_ordering
from app.domain.base import ValueObject


@total_ordering
@dataclass(frozen=True, slots=True, repr=False)
class Token(ValueObject):
    """raises DomainFieldError"""
    
    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(Token, self).__post_init__()
        self._validate_token_type(self.value)
    
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
        

    def _validate_token_type(self, token_value: Decimal) -> None:
        if not isinstance(token_value, Decimal):
            raise DomainFieldError(
                f"Token must be a Decimal, but got {type(token_value)}.",
            )