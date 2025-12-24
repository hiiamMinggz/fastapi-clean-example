# Repository Guidelines

## Project Structure & Module Organization
- `src/app`: layered codebase following Clean Architecture with `domain`, `application`, `infrastructure`, `presentation`, and `setup` (IOC/config, app factory). Entry point: `src/app/run.py`.
- `tests`: pytest suites; markers include `slow` (excluded by default via `-m 'not slow'`).
- `config`: env-specific Docker and settings; `.env.<env>` generated here.
- `alembic`: database migrations; `alembic.ini` configured for CLI usage.
- `scripts`: helpers for Docker pruning, dependency plots, and cleanup; `Makefile` wraps common tasks.

## Setup, Build, and Run
- Python 3.13; recommended to install with `uv python install 3.13` and deps via `uv pip install -e '.[dev,test]'`.
- Export `APP_ENV` (`local`/`dev`/`prod`) before any Make targets; `make env` verifies.
- Generate env file: `make dotenv` (writes `.env.<APP_ENV>` under `config/<APP_ENV>`).
- Local with Docker db only: `make up.db` then `alembic upgrade head`; run FastAPI via IDE/CLI using the same `APP_ENV`.
- Full stack via Docker Compose: `make up` (auto-applies migrations); stop with `make down` or `make down.total` to remove volumes.
- Inspect logs: `make logs.db`; prune Docker cache: `make prune`.

## Coding Style & Naming Conventions
- Python only; 4-space indent, 88-char lines (`ruff` formatter).
- Static checks: `make code.lint` runs `ruff check --exit-non-zero-on-fix`, `slotscheck src`, `mypy` (strict, pydantic + SQLAlchemy plugins).
- Module patterns: value objects immutable where possible; entities rich enough to enforce invariants; keep framework details out of `domain`/`application`.
- Naming: modules snake_case, classes PascalCase, functions/vars snake_case; keep domain language consistent across layers.

## Testing Guidelines
- Default command: `make code.test` (aliases `pytest -v -m 'not slow'`); run slow tests explicitly with `pytest -m slow`.
- Coverage: `make code.cov` (text) or `make code.cov.html` for HTML report.
- Prefer unit tests near corresponding package in `tests`; mirror module paths. Name test files `test_<feature>.py`; parametrize for variants.

## Commit & Pull Request Guidelines
- Commit messages: short, present-tense, imperative (e.g., `add wallet` style used in history); keep scope tight.
- Before pushing: `make code.check` to format/lint/test; ensure migrations are applied and Alembic revision files committed when schema changes.
- PRs: describe intent, affected layers, and env (`APP_ENV`) assumptions; link issues if any; attach API/log snippets or screenshots when behavior changes.

## Security & Configuration Tips
- Never commit secrets; generated `.env.*` files stay under `config/<env>` and should be gitignored.
- Keep `APP_ENV` consistent across app, tests, and Docker to avoid config drift.
- Database changes require matching Alembic migration under `alembic/versions`; avoid direct schema edits in runtime code.
