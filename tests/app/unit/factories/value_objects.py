from decimal import Decimal
import random
from dataclasses import dataclass
from uuid import UUID
import uuid6

from app.domain.base import ValueObject
from app.domain.challenge.value_objects import ChallengeAmount, Description, Title
from app.domain.shared.enums import ProductType
from app.domain.user.value_objects import Email, RawPassword, StreamerChallengeFixedAmount
from app.domain.shared.value_objects.id import ProductId, UserId
from app.domain.user.value_objects import UserPasswordHash
from app.domain.user.value_objects import Username
from app.domain.shared.value_objects.token import Token
from app.domain.shared.entities.transaction.value_objects import ProductId, TransactionId

from app.domain.shared.entities.ledger.value_objects import UserId, EntryId

@dataclass(frozen=True, slots=True, repr=False)
class SingleFieldVO(ValueObject):
    value: int


@dataclass(frozen=True, slots=True, repr=False)
class MultiFieldVO(ValueObject):
    value1: int
    value2: str


def create_single_field_vo(value: int = 1) -> SingleFieldVO:
    return SingleFieldVO(value)


def create_multi_field_vo(value1: int = 1, value2: str = "Viewer") -> MultiFieldVO:
    return MultiFieldVO(value1, value2)


def create_id(value: UUID | None = None) -> UserId:
    return UserId(value if value else uuid6.uuid7())


def create_username(value: str = "Viewer") -> Username:
    return Username(value)


def create_raw_password(value: str = "Good Password") -> RawPassword:
    return RawPassword(value)


def create_password_hash(value: bytes = b"password_hash") -> UserPasswordHash:
    return UserPasswordHash(value)

def create_email(value: str = "viewer@example.com") -> Email:
    return Email(value)

def create_challenge_amount(value: Decimal = '10000') -> ChallengeAmount:
    return ChallengeAmount(value)

def create_challenge_id(value: UUID | None = None) -> ProductId:
    return ProductId(value or uuid6.uuid7())

def create_title(value: str = "Challenge Title") -> Title:
    return Title(value)

def create_description(value: str | None = "Complete the task") -> Description:
    return Description(value)

def create_streamer_fixed_amount(
    value: Decimal = Decimal("10.00"),
) -> StreamerChallengeFixedAmount:
    return StreamerChallengeFixedAmount(value)

def create_token(value: Decimal = Decimal("10.00")) -> Token:
    return Token(value)

def create_transaction_id(value: UUID | None = None) -> TransactionId:
    return TransactionId(value or uuid6.uuid7())

def create_reference_id(value: UUID | None = None) -> ProductId:
    return ProductId(value or uuid6.uuid7())

def create_account_id(value: UUID | None = None) -> UserId:
    return UserId(value or uuid6.uuid7())

def create_entry_id(value: UUID | None = None) -> EntryId:
    return EntryId(value or uuid6.uuid7())

def create_reference_type() -> ProductType:
    return random.choice(list(ProductType))
