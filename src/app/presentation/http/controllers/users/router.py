from fastapi import APIRouter

from app.presentation.http.controllers.users.activate_user import (
    create_activate_user_router,
)
from app.presentation.http.controllers.users.apply_as_streamer import create_apply_as_streamer_router
from app.presentation.http.controllers.users.change_password import (
    create_change_password_router,
)
from app.presentation.http.controllers.users.deactivate_user import (
    create_deactivate_user_router,
)
from app.presentation.http.controllers.users.list_users import create_list_users_router


def create_users_router() -> APIRouter:
    router = APIRouter(
        prefix="/users",
        tags=["Users"],
    )

    sub_routers = (
        create_list_users_router(),
        create_change_password_router(),
        create_activate_user_router(),
        create_deactivate_user_router(),
        create_apply_as_streamer_router(),
    )

    for sub_router in sub_routers:
        router.include_router(sub_router)

    return router
