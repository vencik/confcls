from __future__ import annotations
from dataclasses import dataclass
import json

from confcls import Configurable


@dataclass
class Configuration(Configurable):
    number: int
    item1: Item1
    fpnum: float = 0.0
    opt_item2: Item2 = None

@dataclass
class Item1:
    foo: int
    bar: float = 1.0

@dataclass
class Item2:
    baz: str


def test_dataclass(tmpdir):
    json_file = f"{tmpdir}/my_obj.json"
    with open(json_file, "w", encoding="utf-8") as config:
        json.dump({
            "__type__" : "tests.test_dataclass.Configuration",
            "item1" : {
                "__type__" : "tests.test_dataclass.Item1",
                "foo" : 345,
                "bar" : 0.5,
            },
            "number" : 123,
        }, config)

    assert Configurable.from_file(json_file) == Configuration(
        number=123,
        item1=Item1(foo=345, bar=0.5),
    )
