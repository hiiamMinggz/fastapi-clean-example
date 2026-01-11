import pytest

from app.domain.base import DomainFieldError
from app.domain.challenge.value_objects import Description

def test_accepts_none() -> None:
    Description(None)
    
def test_accepts_string() -> None:
    Description("This is a valid description.")
    
def test_accepts_boundary_length() -> None:
    description = "a" * Description.MIN_LEN

    Description(description)


def test_rejects_out_of_bounds_length() -> None:
    description = "a" * (Description.MIN_LEN - 1)

    with pytest.raises(DomainFieldError):
        Description(description)

def test_rejects_non_string() -> None:
    with pytest.raises(DomainFieldError):
        Description(123)  # type: ignore