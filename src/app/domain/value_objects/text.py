from dataclasses import dataclass
from typing import ClassVar, Final

from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class Title(ValueObject):
    """raises DomainFieldError"""

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 255

    value: str

    def __post_init__(self) -> None:
        """:raises DomainFieldError:"""
        super(Title, self).__post_init__()
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
        super(Title, self).__post_init__()
        self._validate_description_length(self.value)

    def _validate_description_length(self, description_value: str) -> None:
        """:raises DomainFieldError:"""
        if len(description_value) < self.MIN_LEN or len(description_value) > self.MAX_LEN:
            raise DomainFieldError(
                f"Title must be between "
                f"{self.MIN_LEN} and "
                f"{self.MAX_LEN} characters.",
            )