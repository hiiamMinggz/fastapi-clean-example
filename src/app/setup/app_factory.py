from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.infrastructure.persistence_sqla.mappings.all import map_tables
from app.presentation.http.auth.asgi_middleware import (
    ASGIAuthMiddleware,
)
from app.setup.config.settings import AppSettings


def create_app() -> FastAPI:
    return FastAPI(
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    map_tables()
    yield None
    await app.state.dishka_container.close()
    # https://dishka.readthedocs.io/en/stable/integrations/fastapi.html


def configure_app(
    app: FastAPI,
    root_router: APIRouter,
    settings: AppSettings,
) -> None:
    app.include_router(root_router)
    app.add_middleware(ASGIAuthMiddleware)
    # https://github.com/encode/starlette/discussions/2451
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Good place to register global exception handlers


def create_async_ioc_container(
    providers: Iterable[Provider],
    settings: AppSettings,
) -> AsyncContainer:
    return make_async_container(
        *providers,
        context={AppSettings: settings},
    )
