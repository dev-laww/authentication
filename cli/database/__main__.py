from __future__ import annotations

import argparse
from typing import Iterable, Optional

from cli.utils import RichLogger
from .helpers import (
    db_execute,
    db_pull,
    db_push,
    migrate_deploy,
    migrate_dev,
    migrate_reset,
)


logger = RichLogger()


def _build_migrate_parser(subparsers: argparse._SubParsersAction) -> None:
    migrate_parser = subparsers.add_parser(
        "migrate",
        help="Migration workflow commands (dev, deploy, reset).",
    )
    migrate_subparsers = migrate_parser.add_subparsers(
        dest="migrate_command", required=True
    )

    dev_parser = migrate_subparsers.add_parser(
        "dev",
        help="Create a new migration and apply it to the development database.",
    )
    dev_parser.add_argument(
        "-n",
        "--name",
        help="Name for the migration (e.g. add_user_profile).",
    )
    dev_parser.add_argument(
        "-c",
        "--create-only",
        action="store_true",
        help="Generate migration files but do not apply them.",
    )
    dev_parser.add_argument(
        "-e",
        "--empty",
        action="store_true",
        help="Create an empty migration without auto-generating changes.",
    )
    dev_parser.add_argument(
        "-s",
        "--skip-seed",
        action="store_true",
        help="Skip running the optional seed script.",
    )

    migrate_subparsers.add_parser(
        "deploy",
        help="Apply all pending migrations to the target database.",
    )

    reset_parser = migrate_subparsers.add_parser(
        "reset",
        help="Drop, recreate, and migrate the database (development).",
    )
    reset_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Skip the confirmation prompt.",
    )
    reset_parser.add_argument(
        "-s",
        "--skip-seed",
        action="store_true",
        help="Skip running the optional seed script.",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m cli database",
        description="Database utilities: migrate (dev/deploy/reset), pull, push, execute.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    _build_migrate_parser(subparsers)

    pull_parser = subparsers.add_parser(
        "pull",
        help="Introspect database into a schema snapshot.",
    )
    pull_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite destination snapshot file.",
    )
    pull_parser.add_argument(
        "-p",
        "--print",
        action="store_true",
        help="Print snapshot to stdout instead of writing a file.",
    )

    push_parser = subparsers.add_parser(
        "push",
        help="Apply schema changes without creating migrations.",
    )
    push_parser.add_argument(
        "-r",
        "--force-reset",
        action="store_true",
        help="Truncate all tables before applying schema changes.",
    )
    push_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Skip confirmation when destructive changes are detected.",
    )

    execute_parser = subparsers.add_parser(
        "execute",
        help="Run raw SQL against the database.",
    )
    execute_parser.add_argument(
        "-f",
        "--file",
        help="Path to a SQL file to execute.",
    )
    execute_parser.add_argument(
        "-s",
        "--stdin",
        action="store_true",
        help="Read SQL statements from stdin.",
    )
    execute_parser.add_argument(
        "-t",
        "--transaction",
        action="store_true",
        help="Execute statements inside a single transaction.",
    )

    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = _build_parser()

    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
    except SystemExit as exc:
        parser.print_help()
        return exc.code if isinstance(exc.code, int) else 1

    try:
        if args.command == "migrate":
            if args.migrate_command == "dev":
                migrate_dev(
                    name=getattr(args, "name", None),
                    create_only=args.create_only,
                    skip_seed=args.skip_seed,
                    empty=args.empty,
                )
            elif args.migrate_command == "deploy":
                migrate_deploy()
            elif args.migrate_command == "reset":
                migrate_reset(
                    force=args.force,
                    skip_seed=args.skip_seed,
                )
        elif args.command == "pull":
            db_pull(force=args.force, print_only=args.print)
        elif args.command == "push":
            db_push(
                force_reset=args.force_reset,
                force=args.force,
            )
        elif args.command == "execute":
            db_execute(
                file_path=args.file,
                use_stdin=args.stdin,
                transactional=args.transaction,
            )
    except Exception as exc:
        logger.error(str(exc))
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
