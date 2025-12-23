from uuid import UUID
from app.domain.shared.value_objects.token import Token
from decimal import Decimal
from typing import ClassVar, Final
from app.domain.base import DomainFieldError, ValueObject
from dataclasses import dataclass

@dataclass(frozen=True, slots=True, repr=False)
class WalletId(ValueObject):
    """raises DomainFieldError"""
    value: UUID
    

@dataclass(frozen=True, slots=True, repr=False)
class Balance(Token):
    """raises DomainFieldError"""
    ZERO: ClassVar[Final[Decimal]] = Decimal("0.00")

    value: Decimal

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(Balance, self).__post_init__()
        self._validate_balance(self.value)

    def _validate_balance(self, balance_value: Decimal) -> None:
        if balance_value < self.ZERO:
            raise DomainFieldError(
                f"Balance must be greater than or equal to {self.ZERO}, but got {balance_value}.",
            )