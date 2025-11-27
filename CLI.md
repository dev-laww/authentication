# CLI Guide

The project ships with a lightweight command line interface available through `python -m cli`. It is bundled with the
codebase, so no global installations are needed.

## Getting Started

```bash
poetry shell              # activate your environment
python -m cli --list      # show available commands
python -m cli --version   # show CLI/build version
python -m cli <cmd> --help
```

### Environment Setup

Set these environment variables before running any command:

| Variable                 | Purpose                                                                              |
|--------------------------|--------------------------------------------------------------------------------------|
| `DATABASE_URL`           | Connection string for the target database (e.g. `postgresql+asyncpg://...`).         |
| `DATABASE_SCHEMA_MODULE` | Module path that imports all models (optional, defaults to `authentication.models`). |

The CLI will refuse to run if Alembic is not configured (`alembic.ini` and `migrations/env.py` must exist) or if these
variables are missing.

## Top-Level Commands

| Command    | Description                                           |
|------------|-------------------------------------------------------|
| `database` | Database workflows: migrate, pull, push, execute SQL. |

Additional commands can be added under `cli/` and will be auto-discovered.

---

## `database` Command

`python -m cli database` exposes everything for schema management and migrations.

### Migrate Workflows

```
python -m cli database migrate dev
# optional: python -m cli database migrate dev --name add_users_table
python -m cli database migrate deploy
python -m cli database migrate reset --force
```

| Subcommand | Purpose                                                 | Key Options                                                             |
|------------|---------------------------------------------------------|-------------------------------------------------------------------------|
| `dev`      | Generate a migration and optionally apply it to dev DB. | `-n/--name`, `-c/--create-only`, `-s/--skip-seed`                       |
| `deploy`   | Apply all pending Alembic migrations to the target DB.  | _(no options)_                                                          |
| `reset`    | Drop, recreate, and migrate the database (dev usage).   | `-f/--force`, `-s/--skip-seed`                                          |

### Schema Workflows

```
python -m cli database pull --force
python -m cli database push --force
python -m cli database execute --file scripts/sql/backfill.sql --transaction
```

| Command   | Purpose                                                                | Key Options                                   |
|-----------|------------------------------------------------------------------------|-----------------------------------------------|
| `pull`    | Introspect the database into a JSON snapshot (`schema.snapshot.json`). | `-f/--force`, `-p/--print`                    |
| `push`    | Sync project metadata to the DB without recording a migration.         | `-r/--force-reset`, `-f/--force`              |
| `execute` | Run raw SQL directly against the database.                             | `-f/--file`, `-s/--stdin`, `-t/--transaction` |

---

## Environment Requirements

- Ensure `DATABASE_URL` is configured (via `.env` or environment variables).
- Run CLI commands from the project root so Alembic paths resolve correctly.

## Adding New Commands

1. Create a new module or package under `cli/` (e.g., `cli/cache/__main__.py`).
2. Implement a `main(argv)` function that returns an exit code.
3. Optionally expose `CLI_DESCRIPTION` for automatic listings.
4. The new command will appear under `python -m cli --list`.
