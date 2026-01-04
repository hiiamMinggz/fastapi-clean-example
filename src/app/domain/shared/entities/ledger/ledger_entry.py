from app.domain.base import Entity
from app.domain.shared.entities.transaction.value_objects import TransactionId
from app.domain.shared.value_objects.time import CreatedAt
from app.domain.shared.value_objects.token import Token
from app.domain.shared.entities.ledger.account_type import AccountType
from app.domain.shared.entities.ledger.value_objects import AccountId, EntryId

class LedgerEntry(Entity[EntryId]):
    def __init__(
        self,
        *, 
        id_: EntryId,
        transaction_id: TransactionId,
        account_type: AccountType,
        account_id: AccountId | None,
        debit: Token,
        credit: Token,
        created_at: CreatedAt,
        ):
        super().__init__(id_=id_)
        self.transaction_id = transaction_id
        self.account_type = account_type
        self.account_id = account_id
        self.debit = debit
        self.credit = credit
        self.created_at = created_at
        self.validate()
    
    def validate(self) -> None:
        if self.debit.value > Token.ZERO and self.credit.value > Token.ZERO:
            raise ValueError("LedgerEntry cannot have both debit and credit > 0")

        if self.debit.value == Token.ZERO and self.credit.value == Token.ZERO:
            raise ValueError("LedgerEntry must have debit or credit > 0")
        

    