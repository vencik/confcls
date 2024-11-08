from __future__ import annotations
from typing import Any, Iterator, Union, ClassVar, Optional
from re import compile as regex_compile, Pattern as RegexPattern, fullmatch


class DotPath:
    """
    Object hierarchy access using dot.separated.path

    This accessor allows selection of objects from hierarchy of objects using
    dot-separated path specification.
    Wildcards are allowed; wildcard `*` in place of list index means "all items",
    in place of dict key or obj. attribute it means "all keys/attributes".
    You may also use slices for list item access (Python syntax) and regular expressions
    in case of attributes/dict keys (e.g. `"foo.r'bar.*'.baz"`).

    E.g. `my_obj.foo.bar.*.baz` would give you `baz` attributes of all `my_obj.foo.bar`
    attributes, `my_obj.my_list.*` will be all `my_list` items and so on...

    Descend is recursive (leaves are produced in depth-first order).
    """

    class Error(Exception):
        """
        Path error
        """

    class Accessible:
        """
        Ancestor of dot-path accessible objects

        Defines `[]` operator which accepts dot-path key and `get` and `items` getters.
        """

        def items(self, key: Union[str, DotPath]) -> Iterator[Any]:
            """
            :param key: Dot-path
            :return: Dot-path and value tuples (like `dict.items` does)
            """
            return (DotPath(key) if isinstance(key, str) else key).items_of(self)

        def get(self, key: Union[str, DotPath], default: Optional[Any] = None) -> Any:
            """
            :param key: Dot-path
            :param default: Default value if nothing lays at the path
            :return: Object at (first) path leaf
            """
            try:
                return next(self.items(key))[1]

            except (StopIteration, IndexError, KeyError, AttributeError):
                return default

        def __getitem__(self, key: Union[str, DotPath]) -> Any:
            """
            :param key: Dot-path
            :return: Object at (first) path leaf
            """
            try:
                return next(self.items(key))[1]

            except (StopIteration, KeyError, AttributeError) as x:
                raise KeyError(
                    f"Nothing found on {key.path if isinstance(key, DotPath) else key}"
                ) from x

    _all_wildcard: ClassVar[RegexPattern] = regex_compile(r".*")
    _slice_regex: ClassVar[RegexPattern] = regex_compile(r"(\d*):(\d*)(:(\d*))?")

    def __init__(self, path: str):
        """
        :param path: Dot-separated path
        """
        self.path = path
        self._path = list(DotPath._parse(f"{path}."))  # to simplify parsing end

    @staticmethod
    def _parse(path: str) -> Iterator[Union[str, int, slice, RegexPattern]]:
        """
        :param path: Dot-path
        :return: Path node object accessors
        """
        regex = ""
        begin = 0
        offset = 0
        while offset < len(path):
            if offset == begin:
                if path[offset] == '.':  # we don't allow empty nodes
                    raise DotPath.Error(f"Empty node specification: {path}:{offset}")

                if (path[offset] == 'r' and offset + 1 < len(path) and
                    path[offset+1] in ("'", '"')
                ):
                    regex = path[offset+1]  # potentially regex, still must end properly
                    offset += 2
                    continue

            if path[offset] == '.':  # end of node (?)
                if regex:
                    if offset > begin + 2 and path[offset-1] == regex:  # regex closed
                        yield DotPath._node2access(path[begin+2:offset-1], regex=True)

                    else:  # the dot is part of the regex
                        offset += 1
                        continue

                else:
                    yield DotPath._node2access(path[begin:offset], regex=False)

                regex = ""
                begin = offset + 1

            offset += 1

        # Unclosed regex
        if regex:
            raise DotPath.Error(f"Regex not closed: {path}:{begin}")

    @staticmethod
    def _node2access(node: str, regex: bool) -> Union[str, int, slice, RegexPattern]:
        """
        :param node: Path node
        :return: Node object accessor
        """
        def int_or_none(arg: Optional[str]) -> Optional[int]:
            return None if arg is None or arg == "" else int(arg)

        if regex:
            return regex_compile(node)

        if node == "*":
            return DotPath._all_wildcard

        if match := fullmatch(DotPath._slice_regex, node):
            return slice(
                int_or_none(match.group(1)),
                int_or_none(match.group(2)),
                int_or_none(match.group(4)),
            )

        try:
            return int(node)  # integer means list index
        except ValueError:
            pass

        return node  # just an ordinary attr. name, apparently

    def _items_of(self, obj: Any, path: list[str]) -> Iterator[tuple[list[str], Any]]:
        """
        `items_of` implementation
        :param obj: Current object
        :param path: Current path
        :return: Dot-path and value tuples
        """
        def fix_index(index: Optional[int], length: int, default: int) -> int:
            if index is None:
                return default

            return length + index if index < 0 else index

        if not len(path) < len(self._path):  # end of path reached
            yield (path, obj)
            return

        access = self._path[len(path)]

        if type(access) in (int, slice):  # object must be list or string
            if type(obj) not in (tuple, list, str):
                raise ValueError(
                    f"Can't use accessor {access} in object {obj} at {path}")

            if isinstance(access, int):  # index
                try:
                    yield from self._items_of(obj[access], path + [str(access)])
                    return

                except IndexError as x:
                    raise IndexError(
                        f"Invalid index {access} for list {obj} at {path}") from x

            if isinstance(access, slice):  # slice
                start = fix_index(access.start, len(obj), 0)
                stop = fix_index(access.stop, len(obj), len(obj))
                step = access.step or 1

                for index in range(start, min(stop, len(obj)), step):
                    yield from self._items_of(obj[index], path + [str(index)])

                return

            raise DotPath.Error(f"Unexpected list {obj} at {path}")

        if isinstance(access, str):  # simple direct attribute / dict key selector
            if isinstance(obj, dict):
                try:
                    yield from self._items_of(obj[access], path + [access])
                    return

                except KeyError as x:
                    raise KeyError(
                        f"Invalid key {access} for dict {obj} at {path}") from x

            # Attribute
            try:
                yield from self._items_of(getattr(obj, access), path + [access])
                return

            except AttributeError as x:
                raise AttributeError(
                    f"Invalid attribute {access} for {obj} at {path}") from x

        assert isinstance(access, RegexPattern)
        if isinstance(obj, dict):
            items = obj.items()
        elif not hasattr(obj, "__dict__"):
            raise KeyError(f"Can't get valid keys from {obj} at {path}")
        else:
            items = obj.__dict__.items()

        for key, value in items:
            if fullmatch(access, key):
                yield from self._items_of(value, path + [key])

    def items_of(self, obj: Any) -> Iterator[tuple[str, Any]]:
        """
        Get items on path from object hierarchy with root `obj`
        :param obj: Object hierarchy root
        :return: Objects on the path (leaves)
        :return: Dot-path and value tuples (like `dict.items` does)
        """
        return (('.'.join(path), value) for path, value in self._items_of(obj, []))
