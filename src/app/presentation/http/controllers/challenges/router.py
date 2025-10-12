from fastapi import APIRouter

from app.presentation.http.controllers.challenges.create_challenge import (
    create_challenge_router,
)
from app.presentation.http.controllers.challenges.update_challenge import (
    update_challenge_router,
)
from app.presentation.http.controllers.challenges.toggle_challenge_status import (
    toggle_challenge_status_router,
)


def create_challenges_router() -> APIRouter:
    router = APIRouter(
        prefix="/challenges",
        tags=["Challenges"],
    )

    sub_routers = (
        create_challenge_router(),
        update_challenge_router(),
        toggle_challenge_status_router(),
        
    )

    for sub_router in sub_routers:
        router.include_router(sub_router)

    return router