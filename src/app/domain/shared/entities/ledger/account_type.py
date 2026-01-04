from enum import StrEnum

class AccountType(StrEnum):
    BANK = "bank"
    USER_WALLET = "user_wallet"
    ESCROW = "escrow"
    COMMISSION = "commission"
