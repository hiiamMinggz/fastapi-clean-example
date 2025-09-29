from fastapi import APIRouter

from app.presentation.http.controllers.challenges.create_challenge import (
    create_create_challenge_router,
)


def create_challenges_router() -> APIRouter:
    router = APIRouter(
        prefix="/challenges",
        tags=["Challenges"],
    )

    sub_routers = (
        create_create_challenge_router(),
    )

    for sub_router in sub_routers:
        router.include_router(sub_router)

    return router