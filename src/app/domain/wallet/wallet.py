from app.domain.base import DomainFieldError, Entity
from app.domain.user.value_objects import UserId
from app.domain.wallet.value_objects import WalletId, Balance
from app.domain.shared.value_objects.time import CreatedAt, UpdatedAt

class Wallet(Entity[WalletId]):
    def __init__(
        self,
        *,
        id_: WalletId,
        owner_id: UserId,
        balance: Balance,
        created_at: CreatedAt,
        updated_at: UpdatedAt | None,
    ) -> None:
        super().__init__(id_=id_)
        self.owner_id = owner_id
        self.balance = balance
        self.created_at = created_at
        self.updated_at = updated_at 
