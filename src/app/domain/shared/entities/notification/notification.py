from app.domain.base import Entity
from app.domain.shared.value_objects.time import CreatedAt, DeliveredAt
from app.domain.shared.value_objects.id import NotificationId, ProductId, UserId

class Notification(Entity[NotificationId]):
    def __init__(
        self,
        *,
        id_: NotificationId,
        product_id: ProductId,
        user_id: UserId,
        title: str,
        message: str,
        created_at: CreatedAt,
        delivered_at: DeliveredAt,
        is_read: bool,
    ) -> None:
        super().__init__(id_=id_)
        self.product_id = product_id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.created_at = created_at
        self.delivered_at = delivered_at
        self.is_read = is_read
  