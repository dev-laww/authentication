import arrow
from fastapi import Request

from ..core.base import Controller
from ..core.response import Response
from ..core.routing.utils import VersionRegistry


class HealthController(Controller):
    """
    Controller for handling health check requests.
    """

    async def check_health(self, request: Request):  # noqa
        registry = VersionRegistry()
        start_time = request.app.state.start_time
        up_time = arrow.utcnow() - start_time

        return Response.ok(
            message="Service is healthy",
            data={
                "status": "healthy",
                "up_time": str(up_time),
                "started_at": start_time.isoformat(),
                "latest_version": str(registry.latest_version),
                "supported_versions": [str(v) for v in registry.all_versions],
            },
        )
