from app.domain.services.wallet import WalletService
from dishka import Provider, Scope, provide

from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.id_generator import IdGenerator
from app.domain.services.streamer_profile import StreamerProfileService
from app.domain.services.user import UserService
from app.domain.services.challenge import ChallengeService
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
    streamer_profile_service = provide(source=StreamerProfileService)
    wallet_service = provide(source=WalletService)
    
    # Ports
    password_hasher = provide(
        source=BcryptPasswordHasher,
        provides=PasswordHasher,
    )
    user_id_generator = provide(
        source=UuidIdGenerator,
        provides=IdGenerator,
    )
