from __future__ import annotations
from dataclasses import dataclass

import pytest

from confcls import DotPath


@dataclass
class A(DotPath.Accessible):
    foo: B
    bar: C
    baz: int


class B:
    def __init__(self):
        self.bar = {"abc": 123, "abd": 124, "bcaaa": 231}
        self.baz = {"ab": "ABC", "bcd": "CDE", "c": "EF"}
        self.l = list(range(10)) + [{"test": "ok"}]

    def __eq__(self, other) -> bool:
        return self.bar == other.bar and self.l == other.l


@dataclass
class C:
    something: str = "whatnot"


def test_str_path():
    a = A(foo=B(), bar=C(), baz=123)

    assert list(DotPath("foo.bar.abd").items_of(a)) == [("foo.bar.abd", 124)]
    assert a["foo.l"] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, {"test": "ok"}]
    assert a["bar.something"] == "whatnot"


def test_int_path():
    a = A(foo=B(), bar=C(), baz=123)

    assert a["foo.l.4"] == 4
    assert a["foo.l.-3"] == 8
    assert a["foo.l.10.test"] == "ok"


def test_slice_path():
    a = A(foo=B(), bar=C(), baz=123)

    assert a["foo.l.3:6"] == 3  # [] operator only gets you the first item
    assert list(a.items("foo.l.3:5")) == [("foo.l.3", 3), ("foo.l.4", 4)]
    assert list(a.items("foo.l.:3")) == [(f"foo.l.{i}", i) for i in (0, 1, 2)]
    assert list(a.items("foo.l.2:8:2")) == [(f"foo.l.{i}", i) for i in (2, 4, 6)]
    assert list(a.items("foo.l.::3")) == [(f"foo.l.{i}", i) for i in (0, 3, 6, 9)]
    assert list(a.items("foo.l.9:")) == [("foo.l.9", 9), ("foo.l.10", {"test": "ok"})]
    assert list(a.items("foo.l.:")) == [
        (f"foo.l.{i}", i) for i in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    ] + [("foo.l.10", {"test": "ok"})]
    assert list(a.items("foo.l.10:.test")) == [("foo.l.10.test", "ok")]


def test_regex_path():
    a = A(foo=B(), bar=C(), baz=123)

    assert list(a.items("r'ba.'")) == [("bar", C()), ("baz", 123)]
    assert list(a.items("foo.bar.r'.*bc.*'")) == [
        ("foo.bar.abc", 123), ("foo.bar.bcaaa", 231),
    ]
    assert list(a.items("foo.baz.*.1")) == [
        ("foo.baz.ab.1", "B"), ("foo.baz.bcd.1", "D"), ("foo.baz.c.1", "F"),
    ]


def test_invalid_path():
    a = A(foo=B(), bar=C(), baz=123)

    with pytest.raises(KeyError):
        a["foo.wrong"]

    with pytest.raises(IndexError):
        a["foo.l.12"]

    with pytest.raises(KeyError):
        a["foo.bar.xyz"]

    with pytest.raises(KeyError):
        a["foo.r'nothing.*'"]

    assert a.get("foo.r'wrong'") is None
    assert a.get("foo.r'wrong'", "right") is "right"
    assert list(a.items("foo.r'wrong'")) == []
