from decimal import Decimal
import re
from typing import ClassVar, Final
from dataclasses import dataclass
from uuid import UUID

from app.domain.base import DomainFieldError, ValueObject
from app.domain.shared.value_objects.token import Token

@dataclass(frozen=True, slots=True, repr=False)
class UserId(ValueObject):
    value: UUID


@dataclass(frozen=True, slots=True, repr=False)
class Email(ValueObject):
    """raises DomainFieldError"""
    
    MIN_LEN: ClassVar[Final[int]] = 5
    MAX_LEN: ClassVar[Final[int]] = 255
    EMAIL_PATTERN: ClassVar[Final[str]] = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    
    value: str

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(Email, self).__post_init__()
        self._validate_email_length(self.value)
        self._validate_email_format(self.value)

    def _validate_email_length(self, email_value: str) -> None:
        """:raises DomainFieldError:"""
        if len(email_value) < self.MIN_LEN or len(email_value) > self.MAX_LEN:
            raise DomainFieldError(
                f"Email must be between "
                f"{self.MIN_LEN} and "
                f"{self.MAX_LEN} characters.",
            )

    def _validate_email_format(self, email_value: str) -> None:
        """:raises DomainFieldError:"""
        if not re.match(self.EMAIL_PATTERN, email_value):
            raise DomainFieldError(
                "Email format is invalid.",
            )

@dataclass(frozen=True, slots=True, repr=False)
class Credibility(ValueObject):
    """raises DomainFieldError"""
    MIN_CREDIBILITY: ClassVar[Final[float]] = 0.0
    MAX_CREDIBILITY: ClassVar[Final[float]] = 5.0
    
    value: float

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(Credibility, self).__post_init__()
        self._validate_credibility(self.value)

    def _validate_credibility(self, credibility_value: float) -> None:
        """:raises DomainFieldError:"""
        if credibility_value < self.MIN_CREDIBILITY or credibility_value > self.MAX_CREDIBILITY:
            raise DomainFieldError(
                f"Credibility must be between "
                f"{self.MIN_CREDIBILITY} and "
                f"{self.MAX_CREDIBILITY}.",
            )
            

@dataclass(frozen=True, slots=True, repr=False)
class RawPassword(ValueObject):
    """raises DomainFieldError"""

    MIN_LEN: ClassVar[Final[int]] = 6

    value: str

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(RawPassword, self).__post_init__()
        self._validate_password_length(self.value)

    def _validate_password_length(self, password_value: str) -> None:
        """:raises DomainFieldError:"""
        if len(password_value) < self.MIN_LEN:
            raise DomainFieldError(
                f"Password must be at least {self.MIN_LEN} characters long.",
            )


@dataclass(frozen=True, slots=True, repr=False)
class UserPasswordHash(ValueObject):
    value: bytes


@dataclass(frozen=True, slots=True, repr=False)
class Username(ValueObject):
    """raises DomainFieldError"""

    MIN_LEN: ClassVar[Final[int]] = 5
    MAX_LEN: ClassVar[Final[int]] = 20

    # Pattern for validating a username:
    # - starts with a letter (A-Z, a-z) or a digit (0-9)
    PATTERN_START: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"^[a-zA-Z0-9]",
    )
    # - can contain multiple special characters . - _ between letters and digits,
    PATTERN_ALLOWED_CHARS: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"[a-zA-Z0-9._-]*",
    )
    #   but only one special character can appear consecutively
    PATTERN_NO_CONSECUTIVE_SPECIALS: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"^[a-zA-Z0-9]+([._-]?[a-zA-Z0-9]+)*[._-]?$",
    )
    # - ends with a letter (A-Z, a-z) or a digit (0-9)
    PATTERN_END: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r".*[a-zA-Z0-9]$",
    )

    value: str

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(Username, self).__post_init__()
        self._validate_username_length(self.value)
        self._validate_username_pattern(self.value)

    def _validate_username_length(self, username_value: str) -> None:
        """:raises DomainFieldError:"""
        if len(username_value) < self.MIN_LEN or len(username_value) > self.MAX_LEN:
            raise DomainFieldError(
                f"Username must be between "
                f"{self.MIN_LEN} and "
                f"{self.MAX_LEN} characters.",
            )

    def _validate_username_pattern(self, username_value: str) -> None:
        """:raises DomainFieldError:"""
        if not re.match(self.PATTERN_START, username_value):
            raise DomainFieldError(
                "Username must start with a letter (A-Z, a-z) or a digit (0-9).",
            )
        if not re.fullmatch(self.PATTERN_ALLOWED_CHARS, username_value):
            raise DomainFieldError(
                "Username can only contain letters (A-Z, a-z), digits (0-9), "
                "dots (.), hyphens (-), and underscores (_).",
            )
        if not re.fullmatch(self.PATTERN_NO_CONSECUTIVE_SPECIALS, username_value):
            raise DomainFieldError(
                "Username cannot contain consecutive special characters"
                " like .., --, or __.",
            )
        if not re.match(self.PATTERN_END, username_value):
            raise DomainFieldError(
                "Username must end with a letter (A-Z, a-z) or a digit (0-9).",
            )


@dataclass(frozen=True, slots=True, repr=False)
class StreamerChallengeFixedAmount(Token):
    """raises DomainFieldError"""
    ZERO: ClassVar[Final[Decimal]] = Decimal("0.00")

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