from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request, status
from fastapi_error_map import ErrorAwareRouter

from app.application.commands.process_payment_webhook import (
    ProcessPaymentWebhookInteractor,
    ProcessPaymentWebhookRequest,
)


def create_payment_webhook_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/webhook/{provider_key}",
        status_code=status.HTTP_200_OK,
    )
    @inject
    async def payment_webhook(
        provider_key: str,
        request: Request,
        interactor: FromDishka[ProcessPaymentWebhookInteractor],
    ) -> None:
        body = await request.body()
        headers = {k: v for k, v in request.headers.items()}
        await interactor.execute(
            ProcessPaymentWebhookRequest(
                provider_key=provider_key,
                headers=headers,
                body=body,
            )
        )

    return router


