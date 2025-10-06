from enum import StrEnum

class UserStatus(StrEnum):
    ACTIVE = "active"
    PENDING = "pending"
    REJECTED = "rejected"