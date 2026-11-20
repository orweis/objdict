import copy
import pickle

import pytest

from objdict import AttrDict, DictUtils, JsDict, Objdict, OrderedMap, Rdict


class TestRdict:
    def test_chained_write(self):
        r = Rdict()
        r["a"]["b"]["c"] = 1
        assert r == {"a": {"b": {"c": 1}}}
        assert isinstance(r["a"]["b"], Rdict)

    def test_missing_read_creates_child(self):
        r = Rdict()
        assert r["x"] == {}
        assert "x" in r

    def test_get_and_in_do_not_create(self):
        r = Rdict()
        assert r.get("x") is None
        assert "x" not in r
        assert len(r) == 0

    def test_constructor_converts_nested_dicts(self):
        r = Rdict({"a": {"b": {"c": 1}}}, d={"e": 2})
        assert isinstance(r["a"], Rdict)
        assert isinstance(r["a"]["b"], Rdict)
        assert isinstance(r["d"], Rdict)
        r["a"]["b"]["x"]["y"] = 1  # chained write works at depth
        assert r["a"]["b"]["x"]["y"] == 1

    def test_constructor_does_not_alias_source_dicts(self):
        src = {"a": {"b": 1}}
        r = Rdict(src)
        r["a"]["b"] = 2
        assert src == {"a": {"b": 1}}

    def test_setitem_converts_plain_dict(self):
        r = Rdict()
        r["a"] = {"b": {"c": 1}}
        assert isinstance(r["a"]["b"], Rdict)

    def test_update_merges_nested_and_extends_lists(self):
        r = Rdict({1: {2: ["a", "b"]}})
        r.update(Rdict({1: {2: ["c", "d"], "2.1": "String"}}))
        assert r == {1: {2: ["a", "b", "c", "d"], "2.1": "String"}}

    def test_update_overrides_scalars_and_type_mismatch(self):
        r = Rdict({"a": 1, "b": {"x": 1}, "c": [1]})
        r.update({"a": 2, "b": 5, "c": {"y": 1}})
        assert r == {"a": 2, "b": 5, "c": {"y": 1}}

    def test_update_keeps_kwargs_with_mapping(self):
        r = Rdict()
        r.update({"a": 1}, b=2)
        assert r == {"a": 1, "b": 2}

    def test_update_accepts_iterable_of_pairs(self):
        r = Rdict()
        r.update([("a", 1), ("b", 2)])
        assert r == {"a": 1, "b": 2}

    def test_update_kwargs_only_and_empty(self):
        r = Rdict()
        r.update(a=1)
        r.update()
        assert r == {"a": 1}

    def test_update_rejects_bad_argument(self):
        with pytest.raises((TypeError, ValueError)):
            Rdict().update(5)

    def test_update_does_not_mutate_callers_lists(self):
        mine = [1, 2]
        theirs = [3]
        r = Rdict({"x": mine})
        r.update({"x": theirs})
        assert r["x"] == [1, 2, 3]
        assert mine == [1, 2]
        assert theirs == [3]

    def test_update_deep_copies_values(self):
        src = {"a": {"b": [1]}}
        r = Rdict()
        r.update(src)
        r["a"]["b"].append(2)
        assert src == {"a": {"b": [1]}}

    def test_update_with_self_is_stable(self):
        r = Rdict({"a": [1], "b": {"c": 1}})
        r.update(r)
        assert r == {"a": [1, 1], "b": {"c": 1}}

    def test_update_converts_plain_nested_current_value(self):
        r = Rdict()
        dict.__setitem__(r, "a", {"x": 1})  # a plain dict slipped in
        r.update({"a": {"y": 2}})
        assert r == {"a": {"x": 1, "y": 2}}
        assert isinstance(r["a"], Rdict)


class TestAttrDict:
    def test_set_get_delete(self):
        d = AttrDict()
        d.a = 1
        assert d["a"] == 1 and d.a == 1
        del d.a
        assert "a" not in d

    def test_missing_attribute_raises(self):
        d = AttrDict()
        with pytest.raises(AttributeError):
            d.nope  # noqa: B018
        with pytest.raises(AttributeError):
            del d.nope

    def test_dunder_probes_raise_and_do_not_create(self):
        d = AttrDict(a=1)
        assert not hasattr(d, "__wrapped__")
        assert d == {"a": 1}

    def test_iteration_and_keys(self):
        d = AttrDict(a=1, b=2)
        assert list(d) == ["a", "b"]


class TestJsDict:
    def test_missing_attribute_is_none(self):
        d = JsDict(a=1)
        assert d.a == 1
        assert d.b is None
        assert "b" not in d

    def test_missing_item_still_raises(self):
        with pytest.raises(KeyError):
            JsDict()["x"]

    def test_dunder_attribute_raises(self):
        assert not hasattr(JsDict(), "__wrapped__")
        assert getattr(JsDict(), "__deepcopy__", "default") == "default"

    def test_copy_works(self):
        d = JsDict(a=[1])
        assert copy.deepcopy(d) == d
        assert copy.copy(d) == d


class TestObjdict:
    def test_recursive_access(self):
        o = Objdict()
        o.a.b.c = 1
        assert isinstance(o.a, Objdict)
        assert isinstance(o.a.b, Objdict)
        assert o.a.b.c == 1

    def test_attribute_assignment_converts_dict(self):
        o = Objdict()
        o.a = {"b": {"c": 1}}
        assert isinstance(o.a, Objdict)
        o.a.b.x.y = 2
        assert o.a.b.x.y == 2

    def test_constructor_converts_nested(self):
        o = Objdict({"a": {"b": 1}})
        assert isinstance(o.a, Objdict)
        assert o.a.b == 1

    def test_delete_attribute(self):
        o = Objdict(a=1)
        del o.a
        assert "a" not in o
        with pytest.raises(AttributeError):
            del o.a

    def test_recursive_update(self):
        o = Objdict()
        o.a.b.c = 1
        o.update({"x": [1, 2, 3]})
        assert isinstance(o.a.b, Objdict)
        assert o.a.b.c == 1
        assert o.x == [1, 2, 3]
        o.update({"x": [4]})
        assert o.x == [1, 2, 3, 4]

    def test_dunder_probe_does_not_create_keys(self):
        o = Objdict(a=1)
        assert not hasattr(o, "__wrapped__")
        assert not hasattr(o, "__html__")
        assert not hasattr(o, "_ipython_display_")
        assert o == {"a": 1}

    def test_dunder_names_are_not_attribute_keys_on_read(self):
        o = Objdict()
        o["__x__"] = 1
        with pytest.raises(AttributeError):
            o.__x__  # noqa: B018
        assert o["__x__"] == 1

    @pytest.mark.parametrize("name", ["__class__", "__dict__", "_dict_type_", "__deepcopy__"])
    def test_setattr_of_special_names_cannot_hijack_object(self, name):
        o = Objdict()
        setattr(o, name, 1)
        assert type(o) is Objdict
        assert o._dict_type_ is Objdict
        assert copy.deepcopy(o) == o
        assert pickle.loads(pickle.dumps(o)) == o  # noqa: S301

    def test_unsafe_dict_type_assignment_is_just_a_key(self):
        o = Objdict()
        o._dict_type_ = lambda: 1 / 0
        o.a.b = 1  # children are still created with the real type
        assert o.a.b == 1

    def test_copy_deepcopy_pickle_roundtrip(self):
        o = Objdict()
        o.a.b = [1, 2]
        for clone in (copy.copy(o), copy.deepcopy(o), pickle.loads(pickle.dumps(o))):  # noqa: S301
            assert clone == o
            assert isinstance(clone, Objdict)
            assert isinstance(clone.a, Objdict)
            clone.c.d = 1  # chaining still works on clones
        assert copy.deepcopy(o).a.b is not o.a.b

    def test_deep_nesting(self):
        o = Objdict()
        node = o
        for _ in range(200):
            node = node.n
        node.leaf = 1
        assert copy.deepcopy(o) == o

    def test_split_groups_and_leftovers_keep_order(self):
        o = Objdict()
        o.a.b.c = 1
        o.d = "2"
        o.another_key = 6
        o.yet_another_key = []
        o.z = 0
        dicts = o.split([("a", "d"), ("another_key",)])
        assert list(dicts[0]) == ["a", "d"]
        assert list(dicts[1]) == ["another_key"]
        assert list(dicts[2]) == ["yet_another_key", "z"]
        assert all(isinstance(d, Objdict) for d in dicts)

    def test_split_missing_key_raises_and_does_not_modify(self):
        o = Objdict(a=1)
        with pytest.raises(KeyError):
            o.split([("nope",)])
        assert o == {"a": 1}

    def test_split_empty_groups(self):
        o = Objdict(a=1)
        assert o.split([]) == [{"a": 1}]
        assert o.split([()]) == [{}, {"a": 1}]


class TestDictUtils:
    def test_split_plain_dict(self):
        assert DictUtils.split({"a": 1, "b": 2, "c": 3}, [("b",)]) == [{"b": 2}, {"a": 1, "c": 3}]

    def test_split_overlapping_groups(self):
        assert DictUtils.split({"a": 1, "b": 2}, [("a",), ("a", "b")]) == [
            {"a": 1},
            {"a": 1, "b": 2},
            {},
        ]

    def test_traverse_string_and_list(self):
        d = {"a": {"b": {"c": 5}}}
        assert DictUtils.traverse(d, "a.b.c") == 5
        assert DictUtils.traverse(d, ["a", "b"]) == {"c": 5}
        assert DictUtils.traverse(d, ("a",)) == {"b": {"c": 5}}
        assert DictUtils.traverse(d, []) is d

    def test_traverse_missing_raises_without_creating(self):
        r = Rdict({"a": {"b": 1}})
        with pytest.raises(KeyError):
            DictUtils.traverse(r, "a.x")
        assert r == {"a": {"b": 1}}

    def test_traverse_bad_path_type(self):
        with pytest.raises(TypeError):
            DictUtils.traverse({}, 5)  # type: ignore[arg-type]


class TestOrderedMap:
    def test_slice_chain_syntax(self):
        m = OrderedMap()
        assert m["a":1]["b":2]["c":3] is m
        assert list(m.items()) == [("a", 1), ("b", 2), ("c", 3)]

    def test_normal_access_and_missing(self):
        m = OrderedMap(a=1)
        assert m["a"] == 1
        with pytest.raises(KeyError):
            m["zz"]

    def test_add_returns_new_and_leaves_operands(self):
        a = OrderedMap([("x", 1)])
        b = {"y": 2}
        c = a + b
        assert isinstance(c, OrderedMap)
        assert list(c.items()) == [("x", 1), ("y", 2)]
        assert dict(a) == {"x": 1}
        assert b == {"y": 2}


def test_pickle_after_setdefault_and_ior():
    import pickle

    for cls in (Objdict, Rdict):
        o = cls()
        o.setdefault("p", {"x": 1})
        o |= {"q": {"y": 2}}
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            assert pickle.loads(pickle.dumps(o, proto)) == o  # noqa: S301


def test_traverse_lists_and_scalars():
    from objdict import DictUtils

    assert DictUtils.traverse({"a": [10, 20]}, ["a", 0]) == 10
    assert DictUtils.traverse({"a": [1, 5]}, ["a", 1]) == 5
    with pytest.raises(KeyError):
        DictUtils.traverse({"a": [10, 20]}, ["a", 7])
    with pytest.raises(KeyError):
        DictUtils.traverse({"a": 1}, "a.b")


def test_update_none_is_noop_and_rdict_child_converted():
    o = Objdict(a=1)
    o.update(None)
    assert o == {"a": 1}
    o.b = Rdict(x=1)
    assert o.b.x == 1
