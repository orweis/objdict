# objdict

A collection of dictionary-like objects for any task. Standard library only.

Requires Python 3.11 or newer (Python 2 is no longer supported; see [CHANGELOG.md](CHANGELOG.md)).

## Install

```bash
pip install git+https://github.com/orweis/objdict
```

To pin a release or commit, append a ref, e.g. `pip install git+https://github.com/orweis/objdict@<tag-or-commit>`.
The last Python 2 code is commit `16d94a1`.

(A PyPI package named `objdict` exists but has not been verified to be this project; install from GitHub.)

## Classes

| Class | What it is |
| --- | --- |
| `Objdict` | All in one: recursively updatable, splittable, attribute accessible, auto-creating children |
| `Rdict` | Recursively updatable dict; reading a missing key creates an empty child |
| `AttrDict` | Access, set and delete items like attributes |
| `JsDict` | Like a JavaScript object: a missing *attribute* reads as `None` |
| `OrderedMap` | An `OrderedDict` with a chainable update syntax |
| `DictUtils` | Static helpers: `split`, `traverse` |

## Usage

```python
>>> from objdict import Objdict
>>> # Create an Objdict and fill it with keys and values through attributes
>>> a = Objdict()
>>> a.x.y = 1
>>> a.x.list = [1, 2, 3]
>>> a
{'x': {'y': 1, 'list': [1, 2, 3]}}
>>> # Another Objdict with similar keys and different values
>>> b = Objdict()
>>> b.anotherKey = "anotherValue"
>>> b.x.list = [4, 5, "6"]
>>> # Merge them: dicts merge recursively, lists are extended
>>> a.update(b)
>>> a
{'x': {'y': 1, 'list': [1, 2, 3, 4, 5, '6']}, 'anotherKey': 'anotherValue'}
>>> a.yet_another_key = None
>>> # Split by keys: "x" in one group, all the rest (in original order) in the last
>>> a.split([("x",)])
[{'x': {'y': 1, 'list': [1, 2, 3, 4, 5, '6']}}, {'anotherKey': 'anotherValue', 'yet_another_key': None}]
>>> from objdict import OrderedMap
>>> OrderedMap()["a":1]["b":2]
OrderedMap({'a': 1, 'b': 2})

```

## Behavior and gotchas

- **Reading a missing key creates it** (`Rdict`/`Objdict`). This enables `o.a.b.c = 1`, but means
  `o.missing`, `o["missing"]` and `hasattr(o, "missing")` all insert `{}`. Use `in` or `.get()` for
  lookups that must not modify the dict, and do not feed untrusted keys to attribute/item reads.
- Names that start and end with `__` are never treated as keys on attribute *read* (they raise
  `AttributeError`), so `copy`, `pickle`, `inspect` and mocks do not create or find keys.
  Use item access for such keys.
- Nested dicts are converted to the container type on construction and assignment.
- `update()` accepts a mapping or iterable of pairs plus keyword arguments. Merged values are
  deep-copied; lists are concatenated into a new list, so the caller's lists are not modified.
- `JsDict` returns `None` for missing attributes only; `d["missing"]` still raises `KeyError`.
- `OrderedMap` slice syntax (`m["a":1]`) sets an item as a side effect and returns the map;
  `m + other` returns a new map.
- Very deeply nested data (about 1000 levels) raises `RecursionError` in `update` and `deepcopy`.
  Not intended for untrusted input; see [SECURITY.md](SECURITY.md).

## Migration from 0.x

See [CHANGELOG.md](CHANGELOG.md) for the full list of breaking changes in 1.0.0.
Notable: Python >= 3.11 only; `update(e=...)` as a keyword now stores a key `'e'`; dunder attribute reads raise `AttributeError`.
`OrderedMap` slice steps are ignored, and `Rdict.copy()`, `fromkeys` and `|` may return plain dicts.

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest            # tests, module docstrings and the README examples
ruff check . && ruff format --check .
mypy
python -m build
```

See [CONTRIBUTING.md](CONTRIBUTING.md). No license file is present in this repository yet.
