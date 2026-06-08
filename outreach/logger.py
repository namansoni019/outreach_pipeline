"""
Structured logging with Rich console output.

Provides a consistent logger for all pipeline stages with colored,
timestamped output. Keeps logs clean and readable.
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.theme import Theme

# Custom theme -- no emojis, clean labels
_THEME = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "bold red",
        "stage": "bold magenta",
        "dim": "dim white",
        "skip": "dim yellow",
        "count": "bold cyan",
    }
)

console = Console(theme=_THEME)


def info(message: str, **kwargs) -> None:
    """Log an informational message."""
    console.print(f"[info][INFO][/info]  {message}", **kwargs)


def success(message: str, **kwargs) -> None:
    """Log a success message."""
    console.print(f"[success][ OK ][/success]  {message}", **kwargs)


def warning(message: str, **kwargs) -> None:
    """Log a warning message."""
    console.print(f"[warning][WARN][/warning]  {message}", **kwargs)


def error(message: str, **kwargs) -> None:
    """Log an error message."""
    console.print(f"[error][ ERR][/error]  {message}", **kwargs)


def stage(name: str, message: str = "", **kwargs) -> None:
    """Log a stage header."""
    console.print(f"\n[stage][STAGE][/stage] {name}", **kwargs)
    if message:
        console.print(f"        {message}")


def dim(message: str, **kwargs) -> None:
    """Log a dimmed/secondary message."""
    console.print(f"[dim]       {message}[/dim]", **kwargs)


def skip(message: str, **kwargs) -> None:
    """Log a skipped-item message (dim yellow)."""
    console.print(f"[skip]  [SKIP][/skip]  {message}", **kwargs)


def separator() -> None:
    """Print a visual separator line."""
    console.print("[dim]" + "-" * 60 + "[/dim]")


def banner(title: str, subtitle: str = "") -> None:
    """Print a startup banner."""
    console.print()
    separator()
    console.print(f"  [bold]{title}[/bold]")
    if subtitle:
        console.print(f"  [dim]{subtitle}[/dim]")
    separator()
    console.print()


def summary_table(summary: dict) -> None:
    """
    Print a final summary table to the console.

    Expects a dict with keys like 'companies_found', 'decision_makers_found', etc.
    """
    table = Table(title="Pipeline Summary", show_lines=False, show_edge=True)
    table.add_column("Metric", style="bold cyan", no_wrap=True)
    table.add_column("Value", justify="right", style="bold white")

    labels = [
        ("Seed Domain", "seed_domain"),
        ("Companies Found", "companies_found"),
        ("Decision Makers", "decision_makers_found"),
        ("Emails Resolved", "emails_resolved"),
        ("Emails Ready", "emails_ready"),
        ("Emails Sent", "emails_sent"),
        ("Failures", "failures_count"),
        ("Run Output", "run_dir"),
    ]
    for label, key in labels:
        val = summary.get(key, "-")
        table.add_row(label, str(val))

    console.print()
    console.print(table)
    console.print()
