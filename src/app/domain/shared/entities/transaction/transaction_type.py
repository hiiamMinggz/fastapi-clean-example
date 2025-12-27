from enum import StrEnum

class TransactionType(StrEnum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"
    ESCROW_LOCK = "escrow_lock"
    ESCROW_RELEASE = "escrow_release"