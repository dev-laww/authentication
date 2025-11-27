from typing import Annotated
from uuid import UUID

from fastapi import Depends

from ..core.base import Controller
from ..core.database import Repository
from ..core.database.repository import get_repository
from ..core.exceptions import ValidationError, NotFoundError
from ..core.response import Response
from ..models import User, Permission, Role, UserPermission
from ..models.user_permission import GrantType


class UserController(Controller):
    def __init__(
        self,
        user_repository: Annotated[Repository[User], Depends(get_repository(User))],
        role_repository: Annotated[Repository[Role], Depends(get_repository(Role))],
        permission_repository: Annotated[
            Repository[Permission], Depends(get_repository(Permission))
        ],
        user_permission_repository: Annotated[
            Repository[UserPermission], Depends(get_repository(UserPermission))
        ],
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.permission_repository = permission_repository
        self.user_permission_repository = user_permission_repository

    async def get_roles(self, user_id: UUID):
        user = await self.user_repository.get(user_id)

        if not user:
            raise NotFoundError("User not found")

        return Response.ok(message="User roles retrieved successfully", data=user.roles)

    async def assign_role(self, user_id: UUID, role_id: UUID):
        user = await self.user_repository.get(user_id)

        if not user:
            raise NotFoundError("User not found")

        role = await self.role_repository.get(role_id)

        if not role:
            raise ValidationError("Role not found")

        if any(r.id == role_id for r in user.roles):
            raise ValidationError("Role already assigned to user")

        updated_roles = [*user.roles, role]

        updated_user = await self.user_repository.update(user.id, roles=updated_roles)

        for permission in role.permissions:
            existing = await self.user_permission_repository.get_first(
                user_id=user_id, permission_id=permission.id
            )

            if existing:
                # If the existing permission is DENY, change it to INHERIT
                if existing.grant_type == GrantType.DENY:
                    await self.user_permission_repository.update(
                        existing.id, grant_type=GrantType.INHERIT
                    )

                continue

            user_permission = UserPermission(
                user_id=user_id,
                permission_id=permission.id,
                grant_type=GrantType.INHERIT,
            )
            await self.user_permission_repository.create(user_permission)

        return Response.ok(
            message="Role assigned to user successfully", data=updated_user.roles
        )

    async def unassign_role(self, user_id: UUID, role_id: UUID):
        user = await self.user_repository.get(user_id)

        if not user:
            raise NotFoundError("User not found")

        role = await self.role_repository.get(role_id)

        if not role:
            raise ValidationError("Role not found")

        if all(r.id != role_id for r in user.roles):
            raise ValidationError("Role not assigned to user")

        updated_roles = [r for r in user.roles if r.id != role_id]

        updated_user = await self.user_repository.update(user.id, roles=updated_roles)

        for permission in role.permissions:
            user_permission = await self.user_permission_repository.get_first(
                user_id=user_id, permission_id=permission.id
            )

            if not user_permission or user_permission.grant_type != GrantType.INHERIT:
                continue

            await self.user_permission_repository.delete(user_permission.id)

        return Response.ok(
            message="Role removed from user successfully", data=updated_user.roles
        )

    async def get_permissions(self, user_id: UUID):
        user = await self.user_repository.get(user_id)

        if not user:
            raise NotFoundError("User not found")

        return Response.ok(
            message="User permissions retrieved successfully",
            data=user.permissions,
        )

    async def assign_permission(
        self,
        user_id: UUID,
        permission_id: UUID,
        grant_type: GrantType = GrantType.GRANT,
    ):
        user = await self.user_repository.get(user_id)

        if not user:
            raise NotFoundError("User not found")

        permission = await self.permission_repository.get(permission_id)

        if not permission:
            raise ValidationError("Permission not found")

        existing = await self.user_permission_repository.get_first(
            user_id=user_id, permission_id=permission_id
        )

        if existing:
            updated = await self.user_permission_repository.update(
                existing.id, grant_type=grant_type
            )
            return Response.ok(
                message=f"Permission {grant_type.value} updated for user successfully",
                data=updated,
            )

        user_permission = UserPermission(
            user_id=user_id,
            permission_id=permission_id,
            grant_type=grant_type,
        )
        user_permission = await self.user_permission_repository.create(user_permission)

        return Response.ok(
            message=f"Permission {grant_type.value} assigned to user successfully",
            data=user_permission,
        )

    async def unassign_permission(self, user_id: UUID, permission_id: UUID):
        user = await self.user_repository.get(user_id)

        if not user:
            raise NotFoundError("User not found")

        # Find the user permission link
        user_permission = await self.user_permission_repository.get_first(
            user_id=user_id, permission_id=permission_id
        )

        if not user_permission:
            raise NotFoundError("Permission not assigned to user")

        # Delete the user permission
        await self.user_permission_repository.delete(user_permission.id)

        return Response.ok(
            message="Permission removed from user successfully", data=None
        )

    async def deny_permission(self, user_id: UUID, permission_id: UUID):
        return await self.assign_permission(user_id, permission_id, GrantType.DENY)

    async def get_user_permission_overrides(self, user_id: UUID):
        user = await self.user_repository.get(user_id)

        if not user:
            raise NotFoundError("User not found")

        user_perms_links = await self.user_permission_repository.all(user_id=user_id)

        overrides = {
            "granted": [
                link.permission
                for link in user_perms_links
                if link.grant_type == GrantType.GRANT
            ],
            "denied": [
                link.permission
                for link in user_perms_links
                if link.grant_type == GrantType.DENY
            ],
            "inherited": [
                link.permission
                for link in user_perms_links
                if link.grant_type == GrantType.INHERIT
            ],
        }

        return Response.ok(
            message="User permission overrides retrieved successfully", data=overrides
        )
