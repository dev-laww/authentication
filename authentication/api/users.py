from typing import Annotated
from uuid import UUID

from fastapi.params import Depends

from ..controllers.user import UserController
from ..core.routing import post, get, delete, patch
from ..core.routing.routers import AppCRUDRouter
from ..models import User


class UsersRouter(AppCRUDRouter[User]):
    controller: Annotated[UserController, Depends()]

    def __init__(self):
        super().__init__(
            prefix="/users",
            model=User,
            include_create=False,
            include_delete=False,
            include_update=False,
            tags=["Users"],
        )

    @get("/{id}/roles")
    async def get_roles(self, id: UUID):
        return await self.controller.get_roles(id)

    @post("/{id}/roles/{role_id}")
    async def assign_role(self, id: UUID, role_id: UUID):
        return await self.controller.assign_role(id, role_id)

    @delete("/{id}/roles/{role_id}")
    async def unassign_role(self, id: UUID, role_id: UUID):
        return await self.controller.unassign_role(id, role_id)

    @get("/{id}/permissions")
    async def get_permissions(self, id: UUID):
        return await self.controller.get_permissions(id)

    @post("/{id}/permissions/{permission_id}")
    async def assign_permission(self, id: UUID, permission_id: UUID):
        return await self.controller.assign_permission(id, permission_id)

    @delete("/{id}/permissions/{permission_id}")
    async def unassign_permission(self, id: UUID, permission_id: UUID):
        return await self.controller.unassign_permission(id, permission_id)

    @patch("/{id}/permissions/{permission_id}/deny")
    async def deny_permission(self, id: UUID, permission_id: UUID):
        return await self.controller.deny_permission(id, permission_id)


router = UsersRouter()
