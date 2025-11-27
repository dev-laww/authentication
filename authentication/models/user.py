from functools import cached_property
from typing import Optional, TYPE_CHECKING, List

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from .user_permission import UserPermission
from .user_role import UserRole
from ..core.base import BaseDBModel

if TYPE_CHECKING:
    from .account import Account
    from .permission import Permission
    from .role import Role
    from .session import Session
    from .verification import Verification


class User(BaseDBModel, table=True):
    __tablename__ = "users"

    email: EmailStr = Field(unique=True, index=True)
    email_verified: bool = Field(default=False)
    image: Optional[str] = Field(default=None)

    roles: List["Role"] = Relationship(
        back_populates="users",
        link_model=UserRole,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    accounts: List["Account"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    sessions: List["Session"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    verifications: List["Verification"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    permissions: List["Permission"] = Relationship(
        back_populates="users",
        link_model=UserPermission,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "User.id == UserPermission.user_id",
            "secondaryjoin": "and_(UserPermission.permission_id == Permission.id, UserPermission.grant_type != 'deny')",
            "viewonly": True,
        },
    )

    @cached_property
    def _permission_names(self):
        return {permission.name for permission in self.permissions}

    def has_permission(self, name: str) -> bool:
        return name in self._permission_names
