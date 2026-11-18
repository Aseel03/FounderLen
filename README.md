# FounderLens

FounderLens is a small startup-finance engine. The first milestone establishes validated configuration and a clean package layout.

## Layout

- `config/`: business decisions and tunable thresholds
- `docs/`: tool contract and project notes
- `src/founderlens/`: installable Python package
- `tests/`: configuration and architecture checks

## Setup

Install [uv](https://docs.astral.sh/uv/) and Python 3.11 or newer, then run:

```powershell
uv sync --dev
uv run pytest
uv run ruff check .
```

Set `FOUNDERLENS_CONFIG_DIR` to load configuration from another directory.
