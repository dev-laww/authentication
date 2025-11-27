from __future__ import annotations

from typing import Iterable, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class RichLogger:
    """
    Thin wrapper around Rich console utilities for consistent CLI logging.
    """

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def success(self, message: str) -> None:
        self.console.print(Panel.fit(message, style="green"))

    def error(self, message: str) -> None:
        self.console.print(Panel.fit(message, style="red"))

    def info(self, message: str) -> None:
        self.console.print(message)

    def steps(self, lines: Iterable[str]) -> None:
        table = Table(show_header=False, box=None, padding=(0, 1))
        for line in lines:
            table.add_row(f"[bold cyan]›[/] {line}")
        self.console.print(table)
