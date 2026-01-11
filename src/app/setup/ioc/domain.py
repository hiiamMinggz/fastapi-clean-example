from dishka import Provider, Scope, provide

from app.domain.challenge.service import ChallengeService
from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.user.ports import PasswordHasher
from app.domain.user.service import UserService
from app.domain.wallet.service import WalletService
from app.domain.shared.entities.ledger.service import LedgerService
from app.domain.shared.entities.transaction.service import TransactionService
from app.infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
)
from app.infrastructure.adapters.id_generator_uuid import (
    UuidIdGenerator,
)

class DomainProvider(Provider):
    scope = Scope.REQUEST

    # Services
    user_service = provide(source=UserService)
    challenge_service = provide(source=ChallengeService)
    wallet_service = provide(source=WalletService)
    ledger_service = provide(source=LedgerService)
    transaction_service = provide(source=TransactionService)
    # Ports
    password_hasher = provide(
        source=BcryptPasswordHasher,
        provides=PasswordHasher,
    )
    user_id_generator = provide(
        source=UuidIdGenerator,
        provides=IdGenerator,
    )
