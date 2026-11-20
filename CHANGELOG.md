# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/); this project uses semantic versioning.

## [1.0.0] - Unreleased

### Breaking changes
- Python 2 is no longer supported (it did not import on Python 3). Requires Python >= 3.11.
- The module is now a package (`src/objdict/`); `import objdict` is unchanged.
- Attribute reads of dunder names (`__x__`) and of `_oleobj_`, `_obj_`, `_ipython_display_`,
  `_getAttributeNames`, `trait_names` raise `AttributeError` instead of creating or returning keys.
  `JsDict` no longer returns `None` for dunder names.
- `Objdict` attribute assignment no longer routes `__class__`, `__dict__`, `__deepcopy__`,
  `__reduce__`, `__reduce_ex__`, `__get__`, `__set__`, `__members__`, `__methods__` to real attributes;
  they are stored as plain keys. `_dict_type_` can no longer be replaced through attribute assignment.
- `DictUtils.split` / `Objdict.split` raise `KeyError` for missing keys (and no longer insert them
  into the source); left-overs keep source order.
- `Rdict.update` merges keyword arguments given alongside a mapping (previously dropped) and
  accepts iterables of pairs; lists are concatenated into a new list rather than mutated in place.
- `Rdict.update` / `Objdict.update`: `e` is now positional-only, so `update(e={...})` stores a key named
  `'e'` instead of merging the mapping. `update(None)` remains a no-op.
- `OrderedMap.__add__` returns a new map instead of mutating the left operand.
- Removed `DictUtils.group_by` (unfinished; it did nothing) and the `NIL` class.

### Fixed
- `DictUtils.traverse` now follows multi-segment paths and no longer creates keys.
- Nested plain dicts passed to constructors or assigned via attributes are converted.

- Pickling works for Rdict/Objdict holding plain nested dicts added via `setdefault`, `|=` or `dict.update`.
- Assigning an `Rdict` (or other dict) that is not of the container's type converts it, so attributes work.

### Added
- Type hints, `py.typed`, `__all__`, `__version__`, pytest suite, ruff/mypy config, GitHub Actions CI,
  SECURITY.md, CONTRIBUTING.md, `.gitignore`.
- Choosing the final version number and publishing is left to the maintainer.
