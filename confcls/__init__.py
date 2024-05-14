from .object import Object
from .configurable import Configurable


class Configuration(Configurable, Object):
    """
    Configurable `confcls.Object` (i.e. configuration root)
    """
