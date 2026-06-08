"""
CLI entry point for the Outreach Pipeline.

Usage:
    python -m outreach.cli run example.com --mode mock --limit 5
    python -m outreach.cli run example.com --mode mock --limit 5 --send --yes
    python -m outreach.cli run example.com --mode real --limit 5 --send
    python -m outreach.cli history
    python -m outreach.cli --help

Options:
    --mode     : "mock" or "real" (default: mock).
    --limit    : Max similar companies to find (default: 5).
    --dry-run  : Generate drafts but do not send (default: True).
    --yes      : Auto-confirm safety checkpoint in mock mode only.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.table import Table

from outreach import __version__
from outreach.config import load_settings
from outreach.pipeline import run_pipeline
from outreach.storage import list_runs
from outreach.utils import sanitize_domain
from outreach import logger

app = typer.Typer(
    name="outreach",
    help="Automated cold outreach pipeline: seed domain -> outreach emails.",
    no_args_is_help=True,
    add_completion=False,
)


def _execute_pipeline(
    domain: str,
    mode: str = "mock",
    limit: int = 5,
    dry_run: bool = True,
    yes: bool = False,
) -> None:
    """Shared pipeline execution logic."""
    # Validate mode
    if mode not in ("mock", "real"):
        logger.error(f"Invalid mode '{mode}'. Must be 'mock' or 'real'.")
        raise typer.Exit(code=1)

    # Sanitize domain
    clean_domain = sanitize_domain(domain)
    if not clean_domain:
        logger.error("Domain cannot be empty.")
        raise typer.Exit(code=1)

    # Load settings
    settings = load_settings()

    # In real mode, check for missing API keys
    if mode == "real":
        missing = settings.validate_for_real_mode()
        if missing:
            logger.error(f"Missing API keys for real mode: {', '.join(missing)}")
            logger.info("Set the keys in .env or use --mode mock.")
            raise typer.Exit(code=1)

        # Real mode always shows safety checkpoint, --yes is ignored
        if yes:
            logger.warning("--yes is ignored in real mode. Safety checkpoint will be shown.")
            yes = False

    # Run the pipeline
    summary = run_pipeline(
        seed_domain=clean_domain,
        settings=settings,
        mode=mode,
        limit=limit,
        dry_run=dry_run,
        auto_confirm=yes,
    )

    logger.info(f"Run dir: {summary.run_dir}")


@app.command()
def run(
    domain: str = typer.Argument(
        ...,
        help="Seed company domain (e.g. stripe.com).",
    ),
    mode: str = typer.Option(
        "mock",
        "--mode",
        "-m",
        help="Pipeline mode: 'mock' or 'real'.",
    ),
    limit: int = typer.Option(
        5,
        "--limit",
        "-l",
        help="Max number of similar companies to discover.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--send",
        help="Dry run (draft only) vs. actually send emails.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Auto-confirm safety checkpoint (mock mode only).",
    ),
) -> None:
    """Run the full outreach pipeline for a seed domain."""
    _execute_pipeline(domain, mode, limit, dry_run, yes)


@app.command()
def history() -> None:
    """Show past pipeline runs."""
    runs = list_runs()

    if not runs:
        logger.info("No past runs found.")
        return

    table = Table(title="Past Runs", show_lines=True)
    table.add_column("Run Dir", style="cyan", no_wrap=True)
    table.add_column("Seed Domain", style="white")
    table.add_column("Companies", justify="right")
    table.add_column("Contacts", justify="right")
    table.add_column("Emails Sent", justify="right")
    table.add_column("Failures", justify="right")

    for r in runs:
        table.add_row(
            r.get("run_dir", "?"),
            r.get("seed_domain", "?"),
            str(r.get("companies_found", "-")),
            str(r.get("emails_resolved", "-")),
            str(r.get("emails_sent", "-")),
            str(r.get("failures_count", "-")),
        )

    logger.console.print(table)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        is_eager=True,
    ),
    # Backward-compatible alias: --domain works but is hidden from help.
    domain: Optional[str] = typer.Option(
        None,
        "--domain",
        "-d",
        hidden=True,
    ),
    mode: str = typer.Option(
        "mock",
        "--mode",
        "-m",
        hidden=True,
    ),
    limit: int = typer.Option(
        5,
        "--limit",
        "-l",
        hidden=True,
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--send",
        hidden=True,
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        hidden=True,
    ),
) -> None:
    """Automated cold outreach pipeline."""
    if version:
        logger.console.print(f"outreach-pipeline v{__version__}")
        raise typer.Exit()

    # Hidden backward-compatible alias: --domain triggers pipeline
    if domain is not None:
        _execute_pipeline(domain, mode, limit, dry_run, yes)
        raise typer.Exit()

    # If no subcommand was invoked and no --domain was given, show help.
    if ctx.invoked_subcommand is None:
        logger.console.print(ctx.get_help())


if __name__ == "__main__":
    app()
