from enum import Enum
from decimal import Decimal

class Fee(Enum):
    CHALLENGE_FEE = Decimal("0.2")
    COMPETITIVE_FEE = Decimal("0.2")
    DONATE_FEE = Decimal("0.1")

print(Fee.CHALLENGE_FEE.value == Fee.COMPETITIVE_FEE)