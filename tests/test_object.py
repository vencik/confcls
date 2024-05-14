import json

from confcls import Object, Configuration


def test_configuration(tmpdir):
    json_file = f"{tmpdir}/my_obj.json"
    with open(json_file, "w", encoding="utf-8") as config:
        json.dump({
            "__type__" : "confcls.Configuration",
            "myarg1" : "whatever you like",
            "myarg2" : {
                "__type__" : "confcls.Object",
                "absolutely" : "anything",
                "really" : 123,
            },
        }, config)

    my_obj = Configuration.from_file(json_file)
    assert isinstance(my_obj, Configuration)
    assert isinstance(my_obj, Object)

    assert my_obj.myarg1 == "whatever you like"

    assert isinstance(my_obj.myarg2, Object)
    assert my_obj.myarg2.absolutely == "anything"
    assert my_obj.myarg2.really == 123


def test_auto_obj(tmpdir):
    json_file = f"{tmpdir}/my_obj.json"
    with open(json_file, "w", encoding="utf-8") as config:
        json.dump({
            "__type__" : "confcls.Configuration",
            "foo" : {
                "bar" : 123,
            },
            "baz" : [{
                "a" : 1,
                "b" : 2,
            }, {
                "c" : 3,
            }],
        }, config)

    my_obj = Configuration.from_file(json_file, auto_obj=True)
    assert isinstance(my_obj, Configuration)

    assert isinstance(my_obj.foo, Object)
    assert my_obj.foo.bar == 123

    assert type(my_obj.baz) is list
    assert len(my_obj.baz) == 2
    assert isinstance(my_obj.baz[0], Object)
    assert isinstance(my_obj.baz[1], Object)
    assert my_obj.baz[0].a == 1
    assert my_obj.baz[0].b == 2
    assert my_obj.baz[1].c == 3
