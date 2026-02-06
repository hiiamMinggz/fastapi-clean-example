from app.domain.base import Entity

from app.domain.shared.value_objects.id import UserId, EntryId
from app.domain.shared.value_objects.token import Token
from app.domain.shared.entities.ledger.account_type import AccountType

class LedgerEntry(Entity[EntryId]):
    def __init__(
        self,
        *, 
        id_: EntryId,
        account_type: AccountType,
        account_id: UserId | None,
        debit: Token,
        credit: Token,
        ):
        super().__init__(id_=id_)
        self.account_type = account_type
        self.account_id = account_id
        self.debit = debit
        self.credit = credit
        self.validate()
    
    def validate(self) -> None:
        if self.debit.value > Token.ZERO and self.credit.value > Token.ZERO:
            raise ValueError("LedgerEntry cannot have both debit and credit > 0")

        if self.debit.value == Token.ZERO and self.credit.value == Token.ZERO:
            raise ValueError("LedgerEntry must have debit or credit > 0")
        