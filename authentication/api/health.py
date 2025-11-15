from typing import Annotated

from fastapi import Depends, Request

from ..controllers.health import HealthController
from ..core.routing import AppRouter, get


class HealthRouter(AppRouter):
    controller: Annotated[HealthController, Depends()]

    @get("")
    async def get_health_status(self, request: Request):
        return await self.controller.check_health(request)


router = HealthRouter(prefix="/health")
