"""
Per-run storage: creates timestamped output folders and writes stage JSON files.

Output structure per run:
    runs/YYYYMMDD-HHMMSS-domain/
        companies.json
        decision_makers.json
        resolved_contacts.json
        email_drafts.json
        send_results.json
        failures.json
        summary.json
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from outreach.config import PROJECT_ROOT
from outreach import logger
from outreach.models import (
    Company,
    DecisionMaker,
    ResolvedContact,
    EmailDraft,
    EmailSendResult,
    StageFailure,
    PipelineRunSummary,
)

# On Vercel the filesystem is read-only except /tmp.
# Set RUNS_DIR_OVERRIDE=/tmp/runs in Vercel Environment Variables.
_runs_override = os.environ.get("RUNS_DIR_OVERRIDE")
RUNS_DIR = Path(_runs_override) if _runs_override else PROJECT_ROOT / "runs"

# Canonical filenames for each stage output
COMPANIES_FILE = "companies.json"
DECISION_MAKERS_FILE = "decision_makers.json"
RESOLVED_CONTACTS_FILE = "resolved_contacts.json"
EMAIL_DRAFTS_FILE = "email_drafts.json"
SEND_RESULTS_FILE = "send_results.json"
FAILURES_FILE = "failures.json"
SUMMARY_FILE = "summary.json"


# ------------------------------------------------------------------ #
# Run Directory
# ------------------------------------------------------------------ #

def create_run_dir(run_id: str) -> Path:
    """Create and return the output directory for a given run."""
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Run directory: {run_dir.relative_to(PROJECT_ROOT)}")
    return run_dir


# ------------------------------------------------------------------ #
# Generic JSON Writer / Reader
# ------------------------------------------------------------------ #

def _serialize(data: Any) -> Any:
    """Convert pydantic models / lists to JSON-safe dicts."""
    if isinstance(data, BaseModel):
        return data.model_dump(mode="json")
    if isinstance(data, list):
        return [_serialize(item) for item in data]
    return data


def save_json(run_dir: Path, filename: str, data: Any) -> Path:
    """
    Write data to a JSON file inside the run directory.

    Args:
        run_dir: Path to the run folder.
        filename: e.g. "companies.json"
        data: list of Pydantic models, a single model, or a plain dict/list.

    Returns:
        Path to the written file.
    """
    filepath = run_dir / filename
    serialized = _serialize(data)
    filepath.write_text(
        json.dumps(serialized, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.dim(f"Saved {filepath.relative_to(PROJECT_ROOT)}")
    return filepath


def load_json(run_dir: Path, filename: str) -> Any:
    """Read a previously written stage JSON file. Returns None if missing."""
    filepath = run_dir / filename
    if not filepath.exists():
        return None
    return json.loads(filepath.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ #
# Typed Save Helpers (one per stage output)
# ------------------------------------------------------------------ #

def save_companies(run_dir: Path, companies: list[Company]) -> Path:
    """Save Stage 1 output."""
    return save_json(run_dir, COMPANIES_FILE, companies)


def save_decision_makers(run_dir: Path, makers: list[DecisionMaker]) -> Path:
    """Save Stage 2 output."""
    return save_json(run_dir, DECISION_MAKERS_FILE, makers)


def save_resolved_contacts(run_dir: Path, contacts: list[ResolvedContact]) -> Path:
    """Save Stage 3 output."""
    return save_json(run_dir, RESOLVED_CONTACTS_FILE, contacts)


def save_email_drafts(run_dir: Path, drafts: list[EmailDraft]) -> Path:
    """Save Stage 4 drafts."""
    return save_json(run_dir, EMAIL_DRAFTS_FILE, drafts)


def save_send_results(run_dir: Path, results: list[EmailSendResult]) -> Path:
    """Save Stage 4 send results."""
    return save_json(run_dir, SEND_RESULTS_FILE, results)


def save_failures(run_dir: Path, failures: list[StageFailure]) -> Path:
    """Save all stage failures."""
    return save_json(run_dir, FAILURES_FILE, failures)


def save_summary(run_dir: Path, summary: PipelineRunSummary) -> Path:
    """Save the run summary."""
    return save_json(run_dir, SUMMARY_FILE, summary)


# ------------------------------------------------------------------ #
# Run History
# ------------------------------------------------------------------ #

def list_runs() -> list[dict]:
    """
    List all past runs by reading summary.json from each run folder.

    Returns a list of summary dicts sorted by most recent first.
    """
    runs: list[dict] = []
    if not RUNS_DIR.exists():
        return runs

    for run_dir in sorted(RUNS_DIR.iterdir(), reverse=True):
        if not run_dir.is_dir() or run_dir.name.startswith("."):
            continue
        summary = load_json(run_dir, SUMMARY_FILE)
        if summary:
            runs.append(summary)
        else:
            runs.append({"run_dir": str(run_dir.name), "status": "incomplete"})

    return runs
