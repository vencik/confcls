from typing import Any
from json import load
from importlib import import_module

try:
    from smart_open import open
except ImportError:  # smart_open isn't available, use common open
    pass

from .object import Object


class Configurable:
    """
    Provides `from_config` class method for object instantiation from configuration file.

    JSON objects containing special meta key `__type__` shall be treated as keyword
    parameters for constructor of the class specified in that key.
    The class specification must be fully qualified, in the following notation:
    `my.module.path::My.Class.Path`
    I.e. module dot-notation specification is separated from class hierarchy dot-notation
    specification by `::`.

    The configuration deserialiser allows for automatic JSON object to config. object
    conversion.
    Configuration object is a free-form object containing the very same members
    as the JSON object contains (accessible via the standard dot syntax).
    By default, this is (naturally) performed for objects containing the special meta key
    `__type__` with value of `confcls.Object`.
    However, if `Configurable.from_config` `auto_obj` parameter is set to `True`,
    this will be done for all JSON objects (unless they specify otherwise in
    the `__type__` meta key).

    Other data (lists, scalars...) are left unchanged.
    """

    class ConfigError(Exception):
        """
        Configuration error
        """

    @classmethod
    def from_config(cls, json_file: str, auto_obj: bool = False):
        """
        Construct class instance based on JSON configuration
        :param json_file: Instance configuration
        :param auto_obj: Whether to allow automatic dict -> config. object conversion
        :return: Instance
        """
        def obj_hook(obj: dict[str, Any]) -> object:
            meta_type = obj.pop("__type__", None)
            if not meta_type:  # type not specified
                return Object(**obj) if auto_obj else obj

            module_spec, class_path = meta_type.rsplit("::", 1)
            cls = import_module(module_spec)
            for class_spec in class_path.split('.'):
                cls = getattr(cls, class_spec)

            return cls(**obj)  # type: ignore

        with open(json_file, "r", encoding="utf-8") as json_fd:
            obj = load(json_fd, object_hook=obj_hook)

            if not isinstance(obj, cls):  # wrong object configuration
                raise Configurable.ConfigError(
                    f"Load error: {json_file} doesn't configure instance of "
                    f"{cls.__module__}.{cls.__qualname__}")

            return obj
