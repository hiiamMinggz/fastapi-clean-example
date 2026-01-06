from enum import StrEnum


class ChallengeStatus(StrEnum):
    PENDING = "pending"
    STREAMER_ACCEPTED = "streamer_accepted"
    STREAMER_REJECTED = "streamer_rejected"
    STREAMER_COMPLETED = "streamer_completed"
    VIEWER_CONFIRMED = "viewer_confirmed"
    VIEWER_REJECTED = "viewer_rejected"
    REFUNDED = "refunded"
    DONE = "done"