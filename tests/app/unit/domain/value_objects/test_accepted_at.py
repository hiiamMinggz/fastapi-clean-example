import pytest

from app.domain.base import DomainFieldError
from app.domain.shared.value_objects.time import AcceptedAt
from datetime import datetime

def test_accepts_none() -> None:
    AcceptedAt(None)
    
def test_accepts_datetime() -> None:
    AcceptedAt(datetime.now())
    
def test_can_compare() -> None:
    now = datetime.now()
    a = AcceptedAt(now)
    b = AcceptedAt(now)
    
    assert a == b
    a = AcceptedAt(datetime.now())
    b = AcceptedAt(datetime.now())
    
    assert a != b
    assert b > a
    
def test_rejects_non_datetime() -> None:
    with pytest.raises(DomainFieldError):
        AcceptedAt("not a datetime")  # type: ignore