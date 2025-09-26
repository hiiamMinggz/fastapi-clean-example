from enum import Enum

class Fee(float, Enum):
    CHALLENGE_FEE = 0.2
    COMPETITIVE_FEE = 0.2
    DONATE_FEE = 0.1
