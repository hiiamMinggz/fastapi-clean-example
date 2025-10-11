from fastapi import APIRouter

from app.presentation.http.controllers.payments.create_payment import (
    create_create_payment_router,
)
from app.presentation.http.controllers.payments.webhook import (
    create_payment_webhook_router,
)


def create_payments_router() -> APIRouter:
    router = APIRouter(
        prefix="/payments",
        tags=["Payments"],
    )

    sub_routers = (
        create_create_payment_router(),
        create_payment_webhook_router(),
    )

    for sub_router in sub_routers:
        router.include_router(sub_router)

    return router


