from pyventus.events import EventLinker
from app.domain.challenge.events import (
    ChallengeCreated,
    ChallengeAcceptedByStreamer,
    ChallengeRejectedByStreamer,
    ChallengeCompletedByStreamer,
    ChallengeConfirmedByViewer,
    ChallengeRejectedByViewer,
)
from app.domain.wallet.service import WalletService
from app.application.common.ports.wallet_command_gateway import WalletCommandGateway

@EventLinker.on(ChallengeCreated)
def debit_viewer_wallet(event: ChallengeCreated):
    pass