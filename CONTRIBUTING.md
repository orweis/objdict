# Contributing

```bash
pip install -e ".[dev]"
pytest && ruff check . && ruff format --check . && mypy
```

Add a test for every behavior change and a CHANGELOG entry for anything user-visible.
