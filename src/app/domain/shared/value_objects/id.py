from dataclasses import dataclass
from uuid import UUID
from app.domain.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class ProductId(ValueObject):
    value: UUID

@dataclass(frozen=True, slots=True, repr=False)
class UserId(ValueObject):
    value: UUID

@dataclass(frozen=True, slots=True, repr=False)
class WalletId(ValueObject):
    """raises DomainFieldError"""
    value: UUID

@dataclass(frozen=True, slots=True, repr=False)
class NotificationId(ValueObject):
    value: UUID

@dataclass(frozen=True, slots=True, repr=False)
class EntryId(ValueObject):
    """raises DomainFieldError"""
    value: UUID


@dataclass(frozen=True, slots=True, repr=False)
class TransactionId(ValueObject):
    value: UUID
