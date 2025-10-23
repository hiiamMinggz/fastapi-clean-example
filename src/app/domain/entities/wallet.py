from app.domain.entities.base import Entity

from app.domain.value_objects.id import UserId
from app.domain.value_objects.token import Balance
from app.domain.value_objects.time import CreatedAt, UpdatedAt

class Wallet(Entity[UserId]):
    def __init__(
        self,
        *,
        id_: UserId,
        balance: Balance,
        created_at: CreatedAt,
        updated_at: UpdatedAt,
    ) -> None:
        super().__init__(id_=id_)
        self.balance = balance
        self.created_at = created_at
        self.updated_at = updated_at
