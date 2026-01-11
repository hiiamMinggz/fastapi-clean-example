import pytest

from app.domain.base import DomainFieldError
from app.domain.user.value_objects import VerifiedBy
from uuid import UUID

def test_accepts_none() -> None:
    VerifiedBy(None)
    
def test_accepts_uuid() -> None:
    VerifiedBy(UUID("12345678-1234-5678-1234-567812345678"))