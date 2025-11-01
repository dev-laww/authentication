from dataclasses import dataclass, field
from typing import Any

from fastapi import APIRouter


@dataclass
class RouterMetadata:
    """
    Container for a discovered router and its associated metadata.

    Attributes:
        router: The APIRouter instance
        metadata: Additional metadata about the router (e.g., tags, descriptions, flags)
    """
    router: APIRouter
    metadata: dict[str, Any] = field(default_factory=dict)
