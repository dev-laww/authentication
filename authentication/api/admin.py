from typing import Annotated

from fastapi import Depends

from ..controllers.admin import AdminController
from ..core.routing import AppRouter
from ..core.routing.routers.crud import AppCRUDRouter
from ..models import Role
from ..schemas.role import UpdateRole, CreateRole


class AdminRouter(AppRouter):
    controller: Annotated[AdminController, Depends()]


async def exists_callback(role: Role, role_repo):
    return await role_repo.exists(name=role.name)


role_router = AppCRUDRouter(
    prefix="/roles",
    model=Role,
    create_schema=CreateRole,
    update_schema=UpdateRole,
    exists_callback=exists_callback,
    tags=["Roles"],
)

router = AdminRouter(prefix="/admin")

router.include_router(role_router)
