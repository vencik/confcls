from .object import Object
from .configurable import Configurable
from .dot_path import DotPath


class Configuration(Configurable, DotPath.Accessible, Object):
    """
    Configurable `confcls.Object` (i.e. configuration root)
    """
