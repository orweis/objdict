"""objdict - a collection of dictionary-like objects for any task.

See the README for an overview and CHANGELOG.md for migration notes.
"""

from __future__ import annotations

import copy
from collections import OrderedDict
from collections.abc import Callable, Hashable, Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Any, TypeVar

__all__ = [
    "AttrDict",
    "AttrObj",
    "DictUtils",
    "JsDict",
    "Objdict",
    "OrderedMap",
    "Rdict",
    "__version__",
]

__version__ = "1.0.0"
__author__ = "OW"

_MISSING = object()
_D = TypeVar("_D", bound=dict)  # type: ignore[type-arg]


def _is_dunder(name: str) -> bool:
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


class AttrObj:
    """Mixin for dict subclasses: access, set and delete items as attributes.

    Names that start and end with a double underscore are never treated as keys on
    read (they raise ``AttributeError``), so protocol probes such as ``copy``,
    ``inspect`` or ``unittest.mock`` neither find nor create bogus items. Use item
    access (``obj["__x__"]``) for such keys.
    """

    __slots__ = ()

    if TYPE_CHECKING:

        def __getitem__(self, key: Any) -> Any: ...
        def __setitem__(self, key: Any, value: Any) -> None: ...
        def __delitem__(self, key: Any) -> None: ...

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name) from None

    def __getattr__(self, name: str) -> Any:
        if _is_dunder(name):
            raise AttributeError(name)
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None


class AttrDict(AttrObj, dict):  # type: ignore[type-arg]
    """A dict whose items are also accessible as attributes."""


class JsDict(AttrDict):
    """A dict that behaves like a JavaScript object.

    Items are accessible as attributes and a missing *attribute* reads as ``None``.
    Item access (``d["missing"]``) still raises ``KeyError``.
    """

    def __getattr__(self, name: str) -> Any:
        if _is_dunder(name):
            raise AttributeError(name)
        return self.get(name, None)


class DictUtils:
    """Static helpers for working with dictionaries."""

    @staticmethod
    def split(
        d: Mapping[Any, Any],
        key_groups: Iterable[Iterable[Hashable]],
        dict_type: Callable[[], Any] = dict,
    ) -> list[Any]:
        """Split ``d`` into one dict per key group plus a final left-overs dict.

        Args:
            d: The mapping to split. It is never modified.
            key_groups: Groups of keys, e.g. ``[(1, 2, 3), ("a", "b")]``.
            dict_type: Factory for the result dicts.

        Returns:
            One dict per group, holding that group's keys and values, followed by a
            dict with all keys not named in any group (in the order of ``d``).

        Raises:
            KeyError: If a requested key is not in ``d``.
        """
        result = []
        handled: set[Hashable] = set()
        for key_group in key_groups:
            outcome = dict_type()
            for key in key_group:
                if key not in d:
                    raise KeyError(key)
                outcome[key] = d[key]
                handled.add(key)
            result.append(outcome)
        left_overs = dict_type()
        for key in d:
            if key not in handled:
                left_overs[key] = d[key]
        result.append(left_overs)
        return result

    @staticmethod
    def traverse(d: Mapping[Any, Any], path: str | Sequence[Any]) -> Any:
        """Return the value at ``path`` (a ``"a.b.c"`` string or a list of keys).

        Raises:
            TypeError: If ``path`` is neither a string nor a list/tuple.
            KeyError: If a segment is missing (the mapping is never modified).
        """
        if isinstance(path, str):
            segments: Sequence[Any] = path.split(".")
        elif isinstance(path, (list, tuple)):
            segments = path
        else:
            raise TypeError(f"Path must be list or string. Not {type(path)}")
        current: Any = d
        for segment in segments:
            if segment not in current:
                raise KeyError(segment)
            current = current[segment]
        return current


class Rdict(dict):  # type: ignore[type-arg]
    """A dict with recursive updates and auto-created children.

    Reading a missing key creates (and stores) an empty child, which allows
    chained writes. Use ``.get()`` or ``in`` for lookups that must not modify the dict.
    Nested plain dicts are converted to ``Rdict`` on construction and assignment.
    Updating merges nested dicts, and extends lists.

    Setting item hierarchy example:
        >>> a = Rdict()
        >>> a["Key"]["AnotherKey"]["YetAnotherKey"] = 8
        >>> print(a)
        {'Key': {'AnotherKey': {'YetAnotherKey': 8}}}

    Updating example:
        >>> o1 = Rdict({1: {2: ["a", "b"]}})
        >>> o2 = Rdict({1: {2: ["c", "d"], "2.1": "String"}})
        >>> o1.update(o2)
        >>> print(o1)
        {1: {2: ['a', 'b', 'c', 'd'], '2.1': 'String'}}
    """

    _dict_type_: Callable[..., Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()
        # The type used to create children; bypasses any attribute routing.
        object.__setattr__(self, "_dict_type_", type(self))
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def __getitem__(self, item: Any) -> Any:
        result = super().get(item, _MISSING)
        if result is _MISSING:
            result = self._dict_type_()
            self[item] = result
        return result

    def __setitem__(self, key: Any, value: Any) -> None:
        if isinstance(value, dict) and not isinstance(value, Rdict):
            value = self._dict_type_(value)
        super().__setitem__(key, value)

    def update(self, e: Any = (), /, **f: Any) -> None:
        """Recursively merge ``e`` (mapping or iterable of pairs) and ``f`` into self.

        Mappings merge into existing mappings, lists extend existing lists (without
        modifying the original list objects), anything else replaces the current
        value. Merged-in values are deep-copied.
        """
        items = e.items() if isinstance(e, Mapping) else dict(e).items()
        for source in (items, f.items()):
            for k, v in list(source):
                self._merge_item(k, v)

    def _merge_item(self, k: Any, v: Any) -> None:
        if k in self:
            current = super().__getitem__(k)
            if isinstance(v, Mapping) and isinstance(current, Mapping):
                if not isinstance(current, Rdict):
                    current = self._dict_type_(current)
                    self[k] = current
                current.update(v)
                return
            if isinstance(v, list) and isinstance(current, list):
                self[k] = current + copy.deepcopy(v)
                return
        self[k] = copy.deepcopy(v)


class Objdict(AttrObj, Rdict):
    """All the dictionary enhancements in one object-dictionary.

    Recursively updatable, splittable and attribute accessible. See the README.
    """

    # Attribute names that are never keys (IDE/shell introspection probes).
    __ignored_keys__ = frozenset(
        {
            "_dict_type_",
            "_oleobj_",
            "_obj_",
            "_ipython_display_",
            "_getAttributeNames",
            "trait_names",
        }
    )

    def __getattr__(self, name: str) -> Any:
        if name in Objdict.__ignored_keys__:
            raise AttributeError(name)
        return AttrObj.__getattr__(self, name)

    def split(self, key_groups: Iterable[Iterable[Hashable]]) -> list[Any]:
        """Split into one Objdict per key group plus a left-overs Objdict.

        See :meth:`DictUtils.split`.
        """
        return DictUtils.split(self, key_groups, dict_type=type(self))


class OrderedMap(OrderedDict):  # type: ignore[type-arg]
    """An OrderedDict with a chainable update syntax.

    ``m["a":1]["b":2]`` sets ``m["a"] = 1`` and ``m["b"] = 2`` and returns ``m``.
    ``m + other`` returns a new OrderedMap and leaves both operands unchanged.

    See https://stackoverflow.com/a/25889274
    """

    def __getitem__(self, index: Any) -> Any:
        if isinstance(index, slice):
            self[index.start] = index.stop
            return self
        return OrderedDict.__getitem__(self, index)

    def __add__(self, other: Mapping[Any, Any]) -> OrderedMap:
        result = self.__class__(self)
        result.update(other)
        return result
