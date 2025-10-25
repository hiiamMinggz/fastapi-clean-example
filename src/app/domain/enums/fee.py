from enum import Enum
from decimal import Decimal

class Fee(Enum):
    DONE_CHALLENGE_FEE = Decimal("0.2")
    FAIL_CHALLENGE_FEE = Decimal("0.1")
    STREAMER_INSPIRIT = Decimal("0.2")
    COMPETITIVE_FEE = Decimal("0.2")
    DONATE_FEE = Decimal("0.1")
