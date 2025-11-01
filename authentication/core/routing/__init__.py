"""Universal auto-discovery file router for FastAPI applications.

This module provides a FileRouter class that automatically discovers and registers
routes from Python modules in any directory structure.

Example usage:
    from fastapi import FastAPI
    from your_project.core.routing import FileRouter, DefaultExtractor

    app = FastAPI()

    # Simple usage - just specify the routes directory
    app.include_router(FileRouter("./routes"))

    # With configuration
    app.include_router(
        FileRouter(
            "./routes",
            prefix="/api/v1",
            tags=["api"]
        )
    )

    # With custom router extraction logic
    class CustomExtractor(Extractor):
        def extract(self, module: Any) -> list[RouterMetadata]:
            routers = []
            if hasattr(module, 'api_router'):
                routers.append(RouterMetadata(router=module.api_router))
            if hasattr(module, 'admin_router'):
                routers.append(RouterMetadata(
                    router=module.admin_router,
                    metadata={'admin': True}
                ))
            return routers

    app.include_router(
        FileRouter(
            "./routes",
            extractor=CustomExtractor()
        )
    )

Requirements:
- Each route file must have a 'router' variable of type APIRouter (default behavior)
- Or provide a custom Extractor subclass to define your own discovery logic

The FileRouter supports:
- Universal structure - works with any project layout
- APIRouter instances (looks for 'router' variable in each module)
- Custom router extraction logic via Extractor classes
- Recursive directory scanning
- Custom include/exclude patterns
- Automatic prefix and tag application
- No dependency on specific module naming or project structure
"""

from .dto import RouterMetadata
from .extractor import *
from .file_router import FileRouter

__all__ = [
    "RouterMetadata",
    "Extractor",
    "DefaultExtractor",
    "MultiRouterExtractor",
    "FileRouter",
]
