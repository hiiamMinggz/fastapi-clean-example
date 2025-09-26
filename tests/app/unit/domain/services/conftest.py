from typing import cast
from unittest.mock import MagicMock, create_autospec

import pytest

from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.id_generator import IdGenerator


@pytest.fixture
def user_id_generator() -> MagicMock:
    return cast(MagicMock, create_autospec(IdGenerator))


@pytest.fixture
def password_hasher() -> MagicMock:
    return cast(MagicMock, create_autospec(PasswordHasher))
