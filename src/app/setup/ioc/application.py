from app.application.commands.challenge.toggle_challenge_status import ToggleChallengeStatusInteractor
from app.application.commands.user.apply_as_streamer import ApplyAsStreamerInteractor
from app.application.common.ports.transaction_command_gateway import TransactionCommandGateway
from app.application.common.ports.wallet_command_gateway import WalletCommandGateway
from app.infrastructure.adapters.transaction_data_mapper_sqla import SqlaTransactionDataMapper
from app.infrastructure.adapters.wallet_data_mapper_sqla import SqlaWalletDataMapper
from dishka import Provider, Scope, provide, provide_all

from app.application.commands.user.activate_user import ActivateUserInteractor
from app.application.commands.user.change_password import ChangePasswordInteractor
from app.application.commands.challenge.create_challenge import CreateChallengeInteractor
from app.application.commands.challenge.update_challenge import UpdateChallengeInteractor
from app.application.commands.user.deactivate_user import DeactivateUserInteractor
from app.application.common.ports.access_revoker import AccessRevoker
from app.application.common.ports.challenge_command_gateway import ChallengeCommandGateway
from app.application.common.ports.flusher import Flusher
from app.application.common.ports.identity_provider import IdentityProvider
from app.application.common.ports.streamer_command_gateway import StreamerCommandGateway
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.ports.user_query_gateway import UserQueryGateway
from app.application.common.services.current_user import CurrentUserService
from app.application.queries.list_users import ListUsersQueryService
from app.infrastructure.adapters.challenge_data_mapper_sqla import SqlaChallengeDataMapper
from app.infrastructure.adapters.main_flusher_sqla import SqlaMainFlusher
from app.infrastructure.adapters.main_transaction_manager_sqla import (
    SqlaMainTransactionManager,
)
from app.infrastructure.adapters.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)
from app.infrastructure.adapters.streamer_data_mapper_sqla import (
    SqlaStreamerDataMapper,
)
from app.infrastructure.adapters.user_reader_sqla import SqlaUserReader
from app.infrastructure.auth.adapters.access_revoker import (
    AuthSessionAccessRevoker,
)
from app.infrastructure.auth.adapters.identity_provider import (
    AuthSessionIdentityProvider,
)


class ApplicationProvider(Provider):
    scope = Scope.REQUEST

    # Services
    services = provide_all(
        CurrentUserService,
    )

    # Ports Auth
    access_revoker = provide(
        source=AuthSessionAccessRevoker,
        provides=AccessRevoker,
    )
    identity_provider = provide(
        source=AuthSessionIdentityProvider,
        provides=IdentityProvider,
    )

    # Ports Persistence
    tx_manager = provide(
        source=SqlaMainTransactionManager,
        provides=TransactionManager,
    )
    flusher = provide(
        source=SqlaMainFlusher,
        provides=Flusher,
    )
    user_command_gateway = provide(
        source=SqlaUserDataMapper,
        provides=UserCommandGateway,
    )
    streamer_command_gateway = provide(
        source=SqlaStreamerDataMapper,
        provides=StreamerCommandGateway,
    )
    user_query_gateway = provide(
        source=SqlaUserReader,
        provides=UserQueryGateway,
    )

    challenge_command_gateway = provide(
        source=SqlaChallengeDataMapper,
        provides=ChallengeCommandGateway,
    )
    
    wallet_command_gateway = provide(
        source=SqlaWalletDataMapper,
        provides=WalletCommandGateway,
    )
    
    transaction_command_gateway = provide(
        source=SqlaTransactionDataMapper,
        provides=TransactionCommandGateway,
    )
    # Commands
    commands = provide_all(
        ActivateUserInteractor,
        ChangePasswordInteractor,
        DeactivateUserInteractor,
        CreateChallengeInteractor,
        UpdateChallengeInteractor,
        ToggleChallengeStatusInteractor,
        ApplyAsStreamerInteractor,
    )

    # Queries
    query_services = provide_all(
        ListUsersQueryService,
    )
