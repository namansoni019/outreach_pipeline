"""
Tests for CLI semantics and documentation constraints.

Canonical commands tested:
    python -m outreach.cli run example.com --mode mock --limit 5
    python -m outreach.cli run example.com --mode mock --limit 5 --send --yes
    python -m outreach.cli run example.com --mode real --limit 5 --send
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from outreach.cli import cli_app
from outreach.storage import RUNS_DIR

runner = CliRunner()


@pytest.fixture(autouse=True)
def ensure_clean_runs():
    """Clear test run directories to ensure clean state."""
    # Just be careful not to delete legitimate runs if tests run in parallel,
    # but for simple tests we'll just check what the CLI creates.
    yield


def test_default_run_stops_before_sending(monkeypatch):
    """
    python -m outreach.cli run example.com --mode mock --limit 5
    Should run stages 1-3, generate drafts, save JSON, NOT send anything.
    """
    result = runner.invoke(cli_app, ["run", "test-default.com", "--mode", "mock", "--limit", "2"])
    assert result.exit_code == 0
    assert "DRY RUN enabled. Stopping before sending." in result.stdout
    assert "Sending outreach emails..." not in result.stdout

    # Verify JSON files are created (find the run dir from output)
    # The run dir should be named something like: YYYYMMDD-HHMMSS-test-default.com
    run_dir_line = [line for line in result.stdout.splitlines() if "Run dir:" in line]
    assert run_dir_line
    run_dir_name = run_dir_line[0].split("Run dir: ")[-1].strip()
    run_dir_path = RUNS_DIR / run_dir_name

    assert run_dir_path.exists()
    assert (run_dir_path / "companies.json").exists()
    assert (run_dir_path / "decision_makers.json").exists()
    assert (run_dir_path / "resolved_contacts.json").exists()
    assert (run_dir_path / "email_drafts.json").exists()

    # send_results.json should exist as an empty list in dry-run
    assert (run_dir_path / "send_results.json").exists()
    send_data = json.loads((run_dir_path / "send_results.json").read_text(encoding="utf-8"))
    assert send_data == []

    # failures.json should always exist
    assert (run_dir_path / "failures.json").exists()

    # summary.json should always exist
    assert (run_dir_path / "summary.json").exists()
    summary = json.loads((run_dir_path / "summary.json").read_text(encoding="utf-8"))
    assert summary["emails_sent"] == 0


def test_mock_simulated_send_with_yes(monkeypatch):
    """
    python -m outreach.cli run example.com --mode mock --limit 5 --send --yes
    Should run full pipeline, skip prompt, and simulate send.
    """
    result = runner.invoke(cli_app, ["run", "test-mock-send.com", "--mode", "mock", "--limit", "2", "--send", "--yes"])
    assert result.exit_code == 0
    assert "Auto-confirming safety checkpoint (--yes passed)." in result.stdout
    assert "Sending outreach emails..." in result.stdout

    # Verify all 7 files exist
    run_dir_line = [line for line in result.stdout.splitlines() if "Run dir:" in line]
    assert run_dir_line
    run_dir_name = run_dir_line[0].split("Run dir: ")[-1].strip()
    run_dir_path = RUNS_DIR / run_dir_name

    assert run_dir_path.exists()
    assert (run_dir_path / "companies.json").exists()
    assert (run_dir_path / "decision_makers.json").exists()
    assert (run_dir_path / "resolved_contacts.json").exists()
    assert (run_dir_path / "email_drafts.json").exists()
    assert (run_dir_path / "send_results.json").exists()
    assert (run_dir_path / "failures.json").exists()
    assert (run_dir_path / "summary.json").exists()

    # send_results.json should have actual results (not empty)
    send_data = json.loads((run_dir_path / "send_results.json").read_text(encoding="utf-8"))
    assert len(send_data) > 0

    # summary should reflect emails_sent > 0
    summary = json.loads((run_dir_path / "summary.json").read_text(encoding="utf-8"))
    assert summary["emails_sent"] > 0


def test_real_mode_ignores_yes(monkeypatch):
    """
    python -m outreach.cli run example.com --mode real --limit 5 --send --yes
    Should warn that --yes is ignored, show checkpoint, and since there's no user input,
    it will likely abort (Typer defaults to False on Confirm.ask during test if not provided stdin, or we simulate 'N').
    """
    # Mock load_settings to return fake keys so real mode doesn't abort early due to missing keys
    from outreach.config import Settings
    fake_settings = Settings(
        OCEAN_API_TOKEN="fake",
        PROSPEO_API_KEY="fake",
        EAZYREACH_API_KEY="fake",
        BREVO_API_KEY="fake",
        BREVO_SENDER_EMAIL="test@example.com",
        SENDER_EMAIL="test@example.com",
        SENDER_NAME="Test",
    )
    monkeypatch.setattr("outreach.cli.load_settings", lambda: fake_settings)

    # Mock the pipeline functions so we don't actually hit APIs during test
    monkeypatch.setattr("outreach.pipeline.OceanClient", lambda *args, **kwargs: None)
    monkeypatch.setattr("outreach.pipeline.ProspeoClient", lambda *args, **kwargs: None)
    monkeypatch.setattr("outreach.pipeline.EazyreachClient", lambda *args, **kwargs: None)
    monkeypatch.setattr("outreach.pipeline.BrevoClient", lambda *args, **kwargs: None)

    # We expect an exception or abort because OceanClient is None and will fail, but the CLI logic for --yes happens before run_pipeline.
    # Actually, the check is in cli.py before run_pipeline.
    
    result = runner.invoke(cli_app, ["run", "test-real.com", "--mode", "real", "--limit", "2", "--send", "--yes"])
    
    # It should warn about --yes being ignored
    assert "--yes is ignored in real mode. Safety checkpoint will be shown." in result.stdout


def test_invalid_domain_does_not_crash():
    """
    python -m outreach.cli run invalid_domain --mode mock --limit 5
    Should not crash. Pipeline should reject the invalid domain gracefully.
    """
    result = runner.invoke(cli_app, ["run", "invalid_domain", "--mode", "mock", "--limit", "5"])
    assert result.exit_code == 0
    assert "Invalid domain" in result.stdout
    # Pipeline should still print a summary table
    assert "Pipeline Summary" in result.stdout


def test_storage_consistency_on_dry_run():
    """
    Verify that a dry-run always produces all 7 JSON files:
    companies.json, decision_makers.json, resolved_contacts.json,
    email_drafts.json, send_results.json, failures.json, summary.json.
    """
    result = runner.invoke(cli_app, ["run", "test-storage.com", "--mode", "mock", "--limit", "2"])
    assert result.exit_code == 0

    run_dir_line = [line for line in result.stdout.splitlines() if "Run dir:" in line]
    assert run_dir_line
    run_dir_name = run_dir_line[0].split("Run dir: ")[-1].strip()
    run_dir_path = RUNS_DIR / run_dir_name

    expected_files = [
        "companies.json",
        "decision_makers.json",
        "resolved_contacts.json",
        "email_drafts.json",
        "send_results.json",
        "failures.json",
        "summary.json",
    ]
    for filename in expected_files:
        filepath = run_dir_path / filename
        assert filepath.exists(), f"Missing: {filename}"
        content = json.loads(filepath.read_text(encoding="utf-8"))
        assert content is not None, f"Empty/null: {filename}"
