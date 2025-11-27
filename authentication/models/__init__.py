from sqlmodel import SQLModel

from .account import Account
from .permission import Permission
from .role import Role
from .role_permission import RolePermission
from .session import Session
from .user import User
from .user_role import UserRole
from .verification import Verification

metadata = SQLModel.metadata

__all__ = [
    "Account",
    "Permission",
    "Role",
    "RolePermission",
    "Session",
    "User",
    "UserRole",
    "Verification",
    "metadata",
]
