from enum import StrEnum

class TransactionType(StrEnum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"
    ESCROW_LOCK = "escrow_lock"
    ESCROW_RELEASE = "escrow_release"
    POOL_DEPOSIT = "pool_deposit"
    POOL_RELEASE = "pool_release"
    