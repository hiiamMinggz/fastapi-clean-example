from app.domain.base import Entity
from app.domain.shared.entities.transaction.value_objects import TransactionId
from app.domain.shared.value_objects.time import CreatedAt
from app.domain.shared.value_objects.token import Token
from app.domain.ledger.account_type import AccountType
from app.domain.ledger.value_objects import AccountId, EntryId

class LedgerEntry(Entity[EntryId]):
    def __init__(
        self,
        *, 
        id_: EntryId,
        transaction_id: TransactionId,
        account_type: AccountType,
        account_id: AccountId | None,
        debit: Token | None,
        credit: Token | None,
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
        if all([self.debit, self.credit]):
            raise ValueError("Ledger Entry cannot have both debit and credit")
        
        if not any([self.debit, self.credit]):
            raise ValueError("Ledger Entry must have either debit or credit")
        
        if self.debit and self.debit < Token.ZERO:
            raise ValueError("Ledger Entry debit must be greater than or equal to 0")
        
        if self.credit and self.credit < Token.ZERO:
            raise ValueError("Ledger Entry credit must be greater than or equal to 0")

    