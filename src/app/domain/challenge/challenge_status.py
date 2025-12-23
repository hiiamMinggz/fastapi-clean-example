from enum import StrEnum


class Status(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    STREAMER_REJECTED = "rejected"
    STREAMER_COMPLETED = "streamer_completed"
    VIEWER_CONFIRMED = "viewer_confirmed"
    VIEWER_REJECTED = "viewer_rejected"
    REFUNDED = "refunded"
    DONE = "done"