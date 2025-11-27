from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import pkgutil
import sys
from pathlib import Path
from typing import Dict, List


CLI_PACKAGE = "cli"
COMMANDS_PATH = Path(__file__).resolve().parent
COMMAND_IGNORES = {"__main__", "utils", "__pycache__"}


def _discover_commands() -> List[Dict[str, str]]:
    """
    Discover available CLI submodules/packages along with descriptions.
    """

    commands: List[Dict[str, str]] = []
    for module_info in pkgutil.iter_modules([str(COMMANDS_PATH)]):
        if module_info.name.startswith("_") or module_info.name in COMMAND_IGNORES:
            continue

        name = module_info.name
        description = _command_description(name)
        commands.append({"name": name, "description": description})

    return sorted(commands, key=lambda item: item["name"])


def _command_description(command: str) -> str:
    module_name = f"{CLI_PACKAGE}.{command}"

    try:
        module = importlib.import_module(module_name)
    except Exception:
        return ""

    return (
        getattr(module, "CLI_DESCRIPTION", None)
        or (module.__doc__ or "").strip()
        or "No description provided."
    )


def _load_command(command: str):
    """
    Import cli.<command> and return its main function.
    """

    module_name = f"{CLI_PACKAGE}.{command}"

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:  # pragma: no cover - runtime feedback
        available = ", ".join(cmd["name"] for cmd in _discover_commands())
        raise SystemExit(
            f"Unknown command '{command}'. Available commands: {available}"
        ) from exc

    if not hasattr(module, "main"):
        raise SystemExit(f"Module '{module_name}' is missing a main(argv) function.")

    return module.main


def _print_command_list(commands: List[Dict[str, str]]) -> None:
    if not commands:
        print("No CLI commands have been registered.")
        return

    max_name = max(len(cmd["name"]) for cmd in commands)
    print("Available commands:")
    for cmd in commands:
        padded = cmd["name"].ljust(max_name)
        description = cmd["description"]
        print(f"  {padded}  {description}")
    print("\nExample: python -m cli <command> --help")


def _resolve_version() -> str:
    try:
        return importlib.metadata.version("authentication")
    except importlib.metadata.PackageNotFoundError:
        return "local-development"


def main(argv: List[str] | None = None) -> int:
    args_list = list(argv) if argv is not None else sys.argv[1:]
    commands = _discover_commands()
    command_names = {cmd["name"] for cmd in commands}

    parser = argparse.ArgumentParser(
        prog="cli",
        description="Project CLI entry point. Use --list to inspect available commands.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        help="Subcommand to execute (see --list for options).",
    )
    parser.add_argument(
        "command_args",
        nargs=argparse.REMAINDER,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all available CLI commands and exit.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="Show CLI version information.",
    )

    parsed = parser.parse_args(args_list)

    if parsed.version:
        print(_resolve_version())
        return 0

    if parsed.list or not parsed.command:
        _print_command_list(commands)
        return 0 if commands else 1

    if parsed.command not in command_names:
        parser.error(
            f"Unknown command '{parsed.command}'. Run `python -m cli --list` to see options."
        )

    remaining = parsed.command_args
    if remaining and remaining[0] == "--":
        remaining = remaining[1:]

    command_main = _load_command(parsed.command)
    return command_main(remaining)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
