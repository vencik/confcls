from __future__ import annotations
import json

from confcls import Configurable


class Comparable:
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class MyClass(Configurable, Comparable):
    def __init__(self, arg1: str, arg2: int, arg3: list[str], arg4: dict[str, float]):
        self.foo = arg1
        self.bar = arg2
        self.baz = [arg4[name] for name in arg3 if name in arg4]


class Class1(Configurable, Comparable):
    def __init__(self, foo: int, bar: Class2, baz: Class3):
        self.foo = foo
        self.bar = bar
        self.baz = baz

class Class2(Configurable, Comparable):
    def __init__(self, arg1: int, arg2: str):
        self.foo = arg1
        self.bar = arg2

class Class3(Configurable, Comparable):
    def __init__(self, arg: Class2):
        self.baz = arg


def test_class_instantiation(tmpdir):
    json_file = f"{tmpdir}/my_obj.json"
    with open(json_file, "w", encoding="utf-8") as config:
        json.dump({
            "__type__" : "tests.test_class.MyClass",
            "arg1" : "Hello world!",
            "arg2" : 123,
            "arg3" : ["abc", "ghi"],
            "arg4" : {
                "abc" : 0.123,
                "def" : 0.987,
            },
        }, config)

    expect_obj = MyClass(
        arg1="Hello world!",
        arg2=123,
        arg3=["abc", "ghi"],
        arg4={
            "abc" : 0.123,
            "def" : 0.987,
        },
    )

    my_obj = MyClass.from_file(json_file)
    assert isinstance(my_obj, MyClass)
    assert my_obj == expect_obj

    my_obj = Configurable.from_file(json_file)
    assert isinstance(my_obj, MyClass)
    assert my_obj == expect_obj


def test_nesting(tmpdir):
    json_file = f"{tmpdir}/my_obj.json"
    with open(json_file, "w", encoding="utf-8") as config:
        json.dump({
            "__type__" : "tests.test_class.Class1",
            "foo" : 123,
            "bar" : {
                "__type__" : "tests.test_class.Class2",
                "arg1" : 345,
                "arg2" : "whatever",
            },
            "baz" : {
                "__type__" : "tests.test_class.Class3",
                "arg" : {
                    "__type__" : "tests.test_class.Class2",
                    "arg1" : 567,
                    "arg2" : "something else",
                }
            },
        }, config)

    assert Configurable.from_file(json_file) == Class1(
        foo=123,
        bar=Class2(arg1=345, arg2="whatever"),
        baz=Class3(arg=Class2(arg1=567, arg2="something else")),
    )
