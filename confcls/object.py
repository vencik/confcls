class FreeFormObject(type):
    """
    Free-form object meta type; an object which allows dynamic addition of members.
    """

    __type__: str

    def __new__(cls, name: str, base, defcl):
        obj = super().__new__(cls, name, base, defcl)
        obj.__type__ = f"{defcl['__module__']}.{defcl['__qualname__']}"
        return obj


class Object(metaclass=FreeFormObject):
    """
    Configuration object
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
