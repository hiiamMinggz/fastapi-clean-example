from unittest.mock import MagicMock

import pytest

from app.domain.challenge.challenge import Challenge
from app.domain.challenge.service import ChallengeService
from tests.app.unit.factories.challenge import (
    create_challenge,
    create_challenge_id,
)