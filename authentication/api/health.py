from classy_fastapi import get

from ..controllers.health import HealthController
from ..core.base import Routable


class HealthRoutable(Routable):
    """
    Routable class for health check endpoints.
    """
    controller: HealthController

    @get("/")
    def root(self):
        return self.controller.check_health()


routable = HealthRoutable(
    controller=HealthController(),
    prefix="/health"
)
