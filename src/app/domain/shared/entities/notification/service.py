
from datetime import datetime, timezone
from app.domain.shared.entities.notification.notification import Notification
from app.domain.shared.ports.id_generator import IdGenerator
from app.domain.shared.value_objects.id import NotificationId, ProductId, UserId
from app.domain.shared.value_objects.time import CreatedAt, DeliveredAt


class NotificationService:
    def __init__(self, notification_id_generator: IdGenerator):
        self._notification_id_generator = notification_id_generator
    
    def create_notification(
        self,
        *,
        product_id: ProductId,
        user_id: UserId,
        title: str,
        message: str,
    ) -> Notification:
        """creates a new Notification instance"""
        notification_id = NotificationId(self._notification_id_generator())
        now = datetime.now(timezone.utc)

        return Notification(
            id_=notification_id,
            product_id=product_id,
            user_id=user_id,
            title=title,
            message=message,
            created_at=CreatedAt(now),
            delivered_at=None,
            is_read=False,
        )
