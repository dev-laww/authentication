from typing import Annotated

from fastapi import Depends

from ..core.base import Controller
from ..core.database import Repository
from ..core.database.repository import get_repository
from ..models import Role, Permission, User


class AdminController(Controller):
    def __init__(
        self,
        role_repository: Annotated[Repository[Role], Depends(get_repository(Role))],
        permission_repository: Annotated[
            Repository[Permission], Depends(get_repository(Permission))
        ],
        user_repository: Annotated[Repository[User], Depends(get_repository(User))],
    ):
        self.role_repository = role_repository
        self.permission_repository = permission_repository
        self.user_repository = user_repository
