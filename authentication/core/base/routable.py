from classy_fastapi import Routable as ClassyRoutable

from . import Controller, AppObject


class Routable(ClassyRoutable, AppObject):
    """
    Abstract base class for routable components in the application.

    This class serves as a blueprint for all routable classes,
    ensuring they inherit common functionality and structure.
    """

    def __init__(self, controller: Controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
