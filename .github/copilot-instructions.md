# Medjool Farm Manager — Repository Instructions

## Architecture
- `app/domain/`: domain models and business concepts.
- `app/application/`: business/application services.
- `app/infrastructure/`: repositories and persistence adapters.
- `app/database/`: SQLite/database setup.
- `app/presentation/`: PySide6 UI only.
- `tests/`: automated tests.

## Frontend
- Arabic-first, RTL.
- Use the shared UI foundation in `app/presentation/`.
- Keep QSS centralized.
- Prefer reusable page shells, cards, tables, toolbars, forms and dialogs.
- Keep 1180x720 usable and avoid horizontal overflow.

## Data safety
- Never bypass services/repositories from UI code for writes.
- Do not change schema for styling.
- Do not delete existing modules or tests.
- SQLite/local operation remains supported.

## Verification
Run after meaningful changes:
`python -m compileall app`
`python -m pytest -q`

## GitHub automation
Preserve all release workflows under `.github/workflows/`. Agentic workflow source is stored as Markdown and can be compiled with `gh aw compile`; normal release/CI automation remains `.yml`.
