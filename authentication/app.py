from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .core.config import settings


def create_app():
    app = FastAPI(
        title=settings.app_name,
        default_response_class=JSONResponse
    )

    @app.get("/")
    async def root():
        return {
            "message": "Authentication Service is running"
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy"
        }

    return app