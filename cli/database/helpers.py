from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional

from alembic import command
from rich.prompt import Confirm
from sqlalchemy import inspect as sa_inspect, text
from sqlalchemy.schema import CreateColumn, MetaData

from cli.utils import RichLogger
from .utils import (
    SEED_SCRIPT,
    build_alembic_config,
    build_async_engine,
    default_schema_snapshot_path,
    ensure_alembic_is_configured,
    load_metadata,
    qualified_table_name,
    recreate_database,
)

logger = RichLogger()


def _maybe_run_seed(skip_seed: bool) -> None:
    if skip_seed:
        logger.info("Skipping seed script (--skip-seed).")
        return

    if not SEED_SCRIPT.exists():
        logger.info("No seed script found at scripts/seed.py; skipping.")
        return

    logger.steps([f"Running seed script: {SEED_SCRIPT}"])
    try:
        subprocess.run([sys.executable, str(SEED_SCRIPT)], check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Seed script failed with exit code {exc.returncode}"
        ) from exc


async def _truncate_all_tables(metadata: MetaData) -> None:
    engine = build_async_engine()
    table_names = [
        qualified_table_name(table.schema, table.name)
        for table in metadata.sorted_tables
    ]

    if not table_names:
        logger.info("No tables registered in metadata; nothing to truncate.")
        await engine.dispose()
        return

    async with engine.begin() as conn:
        joined = ", ".join(table_names)
        logger.steps([f"Truncating tables: {joined}"])
        await conn.execute(text(f"TRUNCATE TABLE {joined} RESTART IDENTITY CASCADE"))

    await engine.dispose()


async def _sync_schema(metadata: MetaData, force_destructive: bool) -> None:
    engine = build_async_engine()
    async with engine.begin() as conn:
        logger.steps(["Synchronizing schema from project metadata"])

        def _sync(connection):
            metadata.create_all(connection)

            inspector = sa_inspect(connection)
            dialect = connection.dialect

            for table in metadata.sorted_tables:
                if not inspector.has_table(table.name, schema=table.schema):
                    continue

                qualified = qualified_table_name(table.schema, table.name)
                actual_columns = inspector.get_columns(table.name, schema=table.schema)
                actual_names = {col["name"] for col in actual_columns}
                expected_names = {col.name for col in table.columns}

                for column in table.columns:
                    if column.name in actual_names:
                        continue

                    column_sql = str(CreateColumn(column).compile(dialect=dialect))
                    logger.steps([f"Adding column {qualified}.{column.name}"])
                    connection.execute(
                        text(f"ALTER TABLE {qualified} ADD COLUMN {column_sql}")
                    )

                pending_drops: List[str] = []
                for column in actual_columns:
                    if column["name"] in expected_names:
                        continue
                    pending_drops.append(column["name"])

                if pending_drops:
                    warning = (
                        f"Tightening schema will drop columns on {qualified}: "
                        + ", ".join(pending_drops)
                    )
                    logger.info(warning)

                    proceed = True
                    if not force_destructive:
                        proceed = Confirm.ask(
                            "[bold yellow]Continue despite potential data loss?[/]",
                            default=False,
                        )
                    else:
                        logger.info("Force flag provided; skipping confirmation.")

                    if not proceed:
                        raise RuntimeError("Schema sync aborted by user.")

                    for col_name in pending_drops:
                        logger.steps([f'Dropping column {qualified}."{col_name}"'])
                        connection.execute(
                            text(
                                f'ALTER TABLE {qualified} DROP COLUMN "{col_name}" CASCADE'
                            )
                        )

        await conn.run_sync(_sync)

    await engine.dispose()


async def _introspect_schema() -> dict:
    engine = build_async_engine()
    async with engine.begin() as conn:

        def _collect(connection):
            inspector = sa_inspect(connection)
            snapshot = {"tables": []}

            skip_schemas = {"pg_catalog", "information_schema"}
            schemas = [s for s in inspector.get_schema_names() if s not in skip_schemas]

            for schema in schemas:
                for table_name in inspector.get_table_names(schema=schema):
                    columns = inspector.get_columns(table_name, schema=schema)
                    snapshot["tables"].append(
                        {
                            "schema": schema,
                            "name": table_name,
                            "columns": [
                                {
                                    "name": col["name"],
                                    "type": str(col["type"]),
                                    "nullable": col["nullable"],
                                    "default": str(col["default"])
                                    if col["default"] is not None
                                    else None,
                                }
                                for col in columns
                            ],
                        }
                    )

            return snapshot

        data = await conn.run_sync(_collect)

    await engine.dispose()
    return data


async def _execute_sql_statements(
    statements: Iterable[str], transactional: bool
) -> None:
    engine = build_async_engine()

    if transactional:
        async with engine.begin() as conn:
            for stmt in statements:
                await conn.execute(text(stmt))
    else:
        async with engine.connect() as conn:
            for stmt in statements:
                await conn.execute(text(stmt))

    await engine.dispose()


def _load_sql_from_sources(file_path: Optional[str], use_stdin: bool) -> str:
    if file_path:
        return Path(file_path).read_text()

    if use_stdin:
        return sys.stdin.read()

    raise ValueError("Provide --file <path> or --stdin to supply SQL statements.")


def migrate_dev(
    name: Optional[str],
    create_only: bool,
    skip_seed: bool,
    empty: bool = False,
) -> None:
    ensure_alembic_is_configured()
    config = build_alembic_config()

    try:
        label = f"'{name}'" if name else "(auto-named)"
        logger.steps([f"Generating migration {label}"])
        command.revision(config, message=name, autogenerate=not empty)

        if create_only or empty:
            logger.info("Skipping database upgrade because of --create-only or --empty.")
        else:
            logger.steps(["Applying latest migrations"])
            command.upgrade(config, "head")

        _maybe_run_seed(skip_seed)
        logger.success("Development migration complete.")
    except Exception as exc:
        logger.error(f"'database migrate dev' failed: {exc}")
        raise


def migrate_deploy() -> None:
    ensure_alembic_is_configured()
    config = build_alembic_config()

    try:
        logger.steps(["Applying pending migrations to target database"])
        command.upgrade(config, "head")
        logger.success("Migrations deployed successfully.")
    except Exception as exc:
        logger.error(f"'database migrate deploy' failed: {exc}")
        raise


def migrate_reset(force: bool, skip_seed: bool) -> None:
    ensure_alembic_is_configured()
    if not force:
        confirmed = Confirm.ask(
            "[bold yellow]This will drop and recreate the database. Continue?[/]",
            default=False,
        )
        if not confirmed:
            logger.info("Aborted.")
            return

    config = build_alembic_config()

    try:
        asyncio.run(recreate_database())
        logger.steps(["Applying migrations after reset"])
        command.upgrade(config, "head")
        _maybe_run_seed(skip_seed)
        logger.success("Database reset complete.")
    except Exception as exc:
        logger.error(f"'database migrate reset' failed: {exc}")
        raise


def db_pull(force: bool, print_only: bool) -> None:
    ensure_alembic_is_configured()
    destination = default_schema_snapshot_path()

    if print_only:
        logger.info("Printing schema snapshot (no file write).")
    elif destination.exists() and not force:
        raise FileExistsError(
            f"{destination} already exists. Use --force to overwrite."
        )

    snapshot = asyncio.run(_introspect_schema())
    payload = json.dumps(snapshot, indent=2)

    if print_only:
        print(payload)
    else:
        destination.write_text(payload)
        logger.success(f"Wrote schema snapshot to {destination}")


def db_push(force_reset: bool, force: bool) -> None:
    ensure_alembic_is_configured()
    metadata = load_metadata()

    try:
        if force_reset:
            logger.steps(["Force reset requested before push"])
            asyncio.run(_truncate_all_tables(metadata))

        asyncio.run(_sync_schema(metadata=metadata, force_destructive=force))
        logger.success("Database schema synced to match project metadata.")
    except Exception as exc:
        logger.error(f"'database push' failed: {exc}")
        raise


def db_execute(file_path: Optional[str], use_stdin: bool, transactional: bool) -> None:
    ensure_alembic_is_configured()
    sql_text = _load_sql_from_sources(file_path, use_stdin)
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]

    if not statements:
        logger.info("No SQL statements detected.")
        return

    try:
        asyncio.run(_execute_sql_statements(statements, transactional))
        logger.success("Executed SQL successfully.")
    except Exception as exc:
        logger.error(f"'database execute' failed: {exc}")
        raise
