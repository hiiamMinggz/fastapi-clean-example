from dataclasses import dataclass

from app.domain.base import DomainFieldError, ValueObject
from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.value_objects.id import WalletId
from app.domain.shared.value_objects.token import Token


@dataclass(frozen=True, slots=True, repr=False)
class Allocation(ValueObject):
    """raises DomainFieldError"""

    payee_type: AccountType
    payee_id: WalletId | None
    amount: Token

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        if self.amount.value <= Token.ZERO:
            raise DomainFieldError(
                f"Allocation amount must be greater than 0, but got {self.amount}.",
            )
        if self.payee_type == AccountType.USER_WALLET and self.payee_id is None:
            raise DomainFieldError(
                "Allocation payee_id must be set for user wallets.",
            )
        if self.payee_type != AccountType.USER_WALLET and self.payee_id is not None:
            raise DomainFieldError(
                "Allocation payee_id must be None for system accounts.",
            )
