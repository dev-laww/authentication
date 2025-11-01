import importlib
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from starlette.routing import Router

from .dto import RouterMetadata
from .extractor import Extractor, DefaultExtractor


class FileRouter(APIRouter):
    """
    A universal router that automatically discovers and registers routes from Python modules.

    This router extends APIRouter and scans a directory for Python files, automatically
    importing and registering any APIRouter instances it finds. It's completely
    structure-agnostic and uses an Extractor to define how routers are discovered.

    Usage:
        app.include_router(FileRouter("./routes"))
    """

    logger = getLogger(__name__)

    def __init__(
        self,
        base_path: str,
        prefix: str = "",
        tags: Optional[list[str]] = None,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
        recursive: bool = True,
        extractor: Optional[Extractor] = None,
        **kwargs
    ) -> None:
        """
        Initialize the FileRouter.

        Args:
            base_path: Base directory path to search for route modules
            prefix: URL prefix to add to all discovered routes
            tags: Tags to add to all discovered routes
            include_patterns: List of glob patterns for files to include
            exclude_patterns: List of glob patterns for files to exclude
            recursive: Whether to search subdirectories recursively
            extractor: Custom Extractor instance for discovering routers in modules.
                If None, uses DefaultExtractor which looks for 'router' variable.
            **kwargs: Additional arguments passed to APIRouter
        """
        super().__init__(prefix=prefix, tags=tags or [], **kwargs)

        self.base_path = Path(base_path).resolve()
        self.include_patterns = include_patterns or ["*.py"]
        self.exclude_patterns = exclude_patterns or ["__pycache__", "*.pyc", "__init__.py"]
        self.recursive = recursive
        self.extractor = extractor or DefaultExtractor()
        self.registered_routes = set()
        self._discovery_stats = {}

        # Automatically discover and register routes on initialization
        self._discover_and_register_routes()

    def _discover_and_register_routes(self) -> None:
        """
        Discover and register all routes from the specified directory.
        """
        self.logger.info("Starting route discovery in: %s", self.base_path)

        self._discovery_stats = {
            "modules_found": 0,
            "routers_registered": 0,
            "errors": []
        }

        if not self.base_path.exists():
            error_msg = f"Base path does not exist: {self.base_path}"
            self.logger.error(error_msg)
            self._discovery_stats["errors"].append(error_msg)
            return

        python_files = self._find_python_files()
        self._discovery_stats["modules_found"] = len(python_files)

        self.logger.info("Found %d Python files to process", len(python_files))

        for file_path in python_files:
            try:
                module_stats = self._process_module(file_path)
                self._discovery_stats["routers_registered"] += module_stats["routers_registered"]
                if module_stats["errors"]:
                    self._discovery_stats["errors"].extend(module_stats["errors"])
            except (ImportError, AttributeError, SyntaxError) as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                self.logger.error(error_msg)
                self._discovery_stats["errors"].append(error_msg)

        self.logger.info(
            "Route discovery completed. Registered %d routers from %d modules",
            self._discovery_stats["routers_registered"],
            self._discovery_stats["modules_found"]
        )

    def _find_python_files(self) -> list[Path]:
        """Find all Python files matching the criteria."""
        python_files: list[Path] = []

        if self.recursive:
            for pattern in self.include_patterns:
                python_files.extend(self.base_path.rglob(pattern))
        else:
            for pattern in self.include_patterns:
                python_files.extend(self.base_path.glob(pattern))

        filtered_files: list[Path] = []
        for file_path in python_files:
            if self._should_include_file(file_path):
                filtered_files.append(file_path)

        return filtered_files

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included based on exclude patterns."""
        file_str = str(file_path)

        for exclude_pattern in self.exclude_patterns:
            if exclude_pattern in file_str or file_path.name == exclude_pattern:
                return False

        return True

    def _process_module(self, file_path: Path) -> dict[str, Any]:
        """Process a single Python module and register any routers found."""
        module_stats: dict[str, Any] = {
            "routers_registered": 0,
            "errors": []
        }

        try:
            module_name = file_path.stem

            if module_name in self.registered_routes:
                return module_stats

            project_root = self._find_project_root(file_path)
            if project_root and str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            try:
                full_module_name = self._get_full_module_name(file_path, project_root)
                module = importlib.import_module(full_module_name)

                # Use the extractor to discover routers
                try:
                    extracted_routers = self.extractor.extract(module)

                    if not extracted_routers:
                        self.logger.debug("No routers extracted from %s", full_module_name)

                    for router_metadata in extracted_routers:
                        if isinstance(router_metadata.router, APIRouter):
                            self._register_router(router_metadata)
                            module_stats["routers_registered"] += 1
                            self.logger.debug(
                                "Registered router from %s with metadata: %s",
                                full_module_name,
                                router_metadata.metadata
                            )
                        else:
                            error_msg = (
                                f"Extractor returned non-APIRouter instance "
                                f"from {full_module_name}: {type(router_metadata.router)}"
                            )
                            self.logger.warning(error_msg)
                            module_stats["errors"].append(error_msg)

                except Exception as e:
                    error_msg = f"Extractor failed for {full_module_name}: {str(e)}"
                    self.logger.error(error_msg)
                    module_stats["errors"].append(error_msg)

                self.registered_routes.add(full_module_name)

            finally:
                if project_root and str(project_root) in sys.path:
                    sys.path.remove(str(project_root))

        except (ImportError, AttributeError, SyntaxError) as e:
            error_msg = f"Error processing module {file_path}: {str(e)}"
            self.logger.error(error_msg)
            module_stats["errors"].append(error_msg)

        return module_stats

    def _find_project_root(self, file_path: Path) -> Optional[Path]:
        """Find the project root by looking for common indicators."""
        current_path = file_path.parent
        indicators = ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "poetry.lock"]

        while current_path != current_path.parent:
            for indicator in indicators:
                if (current_path / indicator).exists():
                    return current_path
            current_path = current_path.parent
        return self.base_path.parent

    @staticmethod
    def _get_full_module_name(file_path: Path, project_root: Optional[Path]) -> str:
        """Get the full module name for importing."""
        if project_root:
            relative_path = file_path.relative_to(project_root)
            module_name = str(relative_path).replace("/", ".").replace("\\", ".").replace(".py", "")
            return module_name
        else:
            return file_path.stem

    def _register_router(self, router_metadata: RouterMetadata) -> None:
        """
        Register a discovered router by including its routes.

        Args:
            router_metadata: RouterMetadata containing the router and its metadata
        """
        router = router_metadata.router

        self.include_router(router)

        self.logger.debug("Registered router routes")

    @property
    def stats(self) -> dict[str, Any]:
        """Get discovery statistics."""
        return self._discovery_stats.copy()
