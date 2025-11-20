from typing import Annotated
from uuid import UUID

from fastapi import Depends

from ..core.base import Controller
from ..core.database import Repository
from ..core.database.repository import get_repository
from ..core.exceptions import NotFoundError, ValidationError
from ..core.response import Response
from ..models import Role, Permission


class RoleController(Controller):
    def __init__(
        self,
        role_repository: Annotated[Repository[Role], Depends(get_repository(Role))],
        permission_repository: Annotated[
            Repository[Permission], Depends(get_repository(Permission))
        ],
    ):
        self.role_repository = role_repository
        self.permission_repository = permission_repository

    async def get_role_permissions(self, id: UUID):
        role = await self.role_repository.get(id)

        if not role:
            raise NotFoundError("Role not found")

        return Response.ok(
            message="Role permissions retrieved successfully", data=role.permissions
        )

    async def assign_permissions_to_role(self, id: UUID, permission_id: UUID):
        role = await self.role_repository.get(id)

        if not role:
            raise NotFoundError("Role not found")

        permission = await self.permission_repository.get(permission_id)

        if not permission:
            raise ValidationError("Permission not found")

        if any(p.id == permission_id for p in role.permissions):
            raise ValidationError("Permission already assigned to role")

        updated_permissions = [*role.permissions, permission]

        updated_role = await self.role_repository.update(
            role.id, permissions=updated_permissions
        )

        return Response.ok(
            message="Permissions assigned to role successfully", data=updated_role
        )

    async def remove_permissions_from_role(self, id: UUID, permission_id: UUID):
        role = await self.role_repository.get(id)

        if not role:
            raise NotFoundError("Role not found")

        if not any(p.id == permission_id for p in role.permissions):
            raise NotFoundError("Permission not assigned to role")

        updated_permissions = [p for p in role.permissions if p.id != permission_id]
        updated_role = await self.role_repository.update(
            role.id, permissions=updated_permissions
        )

        return Response.ok(
            message="Permissions removed from role successfully", data=updated_role
        )
