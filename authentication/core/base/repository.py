from abc import ABC

from .app import AppObject


class Repository(AppObject, ABC):
    """
    Abstract base class for repositories in the application.

    This class serves as a blueprint for all repository classes,
    ensuring they inherit common functionality and structure.
    """
    pass
