from typing import Optional, List
from uuid import UUID

from ..core.base import BaseModel


class CreateRole(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


UpdateRole = CreateRole.make_fields_optional("UpdateRole")


class UpdatePermissions(BaseModel):
    permission_ids: List[UUID]
