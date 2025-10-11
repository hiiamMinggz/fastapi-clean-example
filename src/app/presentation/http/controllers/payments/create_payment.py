from inspect import getdoc
from decimal import Decimal
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from app.application.commands.create_payment import (
    CreatePaymentInteractor,
    CreatePaymentRequest,
    CreatePaymentResponse,
)
from app.domain.exceptions.base import DomainFieldError
from app.domain.value_objects.token import PaymentAmount
from app.presentation.http.auth.fastapi_openapi_markers import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import (
    ServiceUnavailableTranslator,
)
from app.infrastructure.exceptions.gateway import DataMapperError


class CreatePaymentRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)

    payer_id: UUID
    payee_id: UUID
    amount: Decimal = Field(..., ge=Decimal("0.00"))
    currency: str = Field(..., min_length=3, max_length=3)
    description: str | None = Field(default=None, max_length=255)


def create_create_payment_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        description=getdoc(CreatePaymentInteractor),
        error_map={
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
            DomainFieldError: rule(
                status=status.HTTP_400_BAD_REQUEST,
                on_error=log_info,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def create_payment(
        request_data_pydantic: CreatePaymentRequestPydantic,
        interactor: FromDishka[CreatePaymentInteractor],
    ) -> CreatePaymentResponse:
        try:
            PaymentAmount(request_data_pydantic.amount)
        except DomainFieldError as e:
            raise DomainFieldError(f"Invalid input: {str(e)}")

        request_data = CreatePaymentRequest(
            payer_id=request_data_pydantic.payer_id,
            payee_id=request_data_pydantic.payee_id,
            amount=request_data_pydantic.amount,
            currency=request_data_pydantic.currency,
            description=request_data_pydantic.description,
        )
        return await interactor.execute(request_data)

    return router


