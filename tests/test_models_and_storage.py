"""
Test: typed models and JSON storage.

Creates sample data for every model, saves to a run folder,
reads it back, and verifies correctness.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from outreach.models import (
    Company,
    DecisionMaker,
    ResolvedContact,
    EmailDraft,
    EmailSendResult,
    StageFailure,
    PipelineRunSummary,
)
from outreach.storage import (
    create_run_dir,
    save_companies,
    save_decision_makers,
    save_resolved_contacts,
    save_email_drafts,
    save_send_results,
    save_failures,
    save_summary,
    load_json,
    RUNS_DIR,
    COMPANIES_FILE,
    DECISION_MAKERS_FILE,
    RESOLVED_CONTACTS_FILE,
    EMAIL_DRAFTS_FILE,
    SEND_RESULTS_FILE,
    FAILURES_FILE,
    SUMMARY_FILE,
)


# ------------------------------------------------------------------ #
# Sample Data Fixtures
# ------------------------------------------------------------------ #

SAMPLE_COMPANIES = [
    Company(domain="acme.com", name="Acme Corp", source="ocean", confidence=0.92),
    Company(domain="globex.com", name="Globex Inc", source="ocean", confidence=0.85),
    Company(domain="initech.com", name="Initech", source="ocean"),
]

SAMPLE_DECISION_MAKERS = [
    DecisionMaker(
        company_domain="acme.com",
        full_name="Alice Johnson",
        title="VP of Sales",
        linkedin_url="https://linkedin.com/in/alicejohnson",
        source="prospeo",
    ),
    DecisionMaker(
        company_domain="globex.com",
        full_name="Bob Smith",
        title="CTO",
        linkedin_url="https://linkedin.com/in/bobsmith",
        source="prospeo",
    ),
]

SAMPLE_CONTACTS = [
    ResolvedContact(
        company_domain="acme.com",
        full_name="Alice Johnson",
        title="VP of Sales",
        linkedin_url="https://linkedin.com/in/alicejohnson",
        email="alice@acme.com",
        verification_status="verified",
        confidence=0.95,
    ),
    ResolvedContact(
        company_domain="globex.com",
        full_name="Bob Smith",
        title="CTO",
        linkedin_url="https://linkedin.com/in/bobsmith",
        email="bob@globex.com",
        verification_status="verified",
        confidence=0.88,
    ),
]

SAMPLE_DRAFTS = [
    EmailDraft(
        to_email="alice@acme.com",
        subject="Quick question for Alice at acme.com",
        body="Hi Alice, I came across Acme Corp and was impressed...",
        contact_name="Alice Johnson",
        company_domain="acme.com",
    ),
    EmailDraft(
        to_email="bob@globex.com",
        subject="Quick question for Bob at globex.com",
        body="Hi Bob, I came across Globex Inc and was impressed...",
        contact_name="Bob Smith",
        company_domain="globex.com",
    ),
]

SAMPLE_RESULTS = [
    EmailSendResult(
        to_email="alice@acme.com",
        status="sent",
        provider_message_id="msg-001",
    ),
    EmailSendResult(
        to_email="bob@globex.com",
        status="dry_run",
    ),
]

SAMPLE_FAILURES = [
    StageFailure(
        stage="eazyreach",
        item="https://linkedin.com/in/unknown",
        error="404 Not Found",
    ),
]


# ------------------------------------------------------------------ #
# Test: Model Instantiation
# ------------------------------------------------------------------ #

class TestModelCreation:
    """Verify that all models can be instantiated with the specified fields."""

    def test_company_with_optional_confidence(self):
        c = Company(domain="test.com", name="Test", source="ocean")
        assert c.confidence is None
        c2 = Company(domain="test.com", name="Test", source="ocean", confidence=0.9)
        assert c2.confidence == 0.9

    def test_decision_maker_fields(self):
        dm = SAMPLE_DECISION_MAKERS[0]
        assert dm.company_domain == "acme.com"
        assert dm.full_name == "Alice Johnson"
        assert dm.title == "VP of Sales"
        assert dm.linkedin_url == "https://linkedin.com/in/alicejohnson"
        assert dm.source == "prospeo"

    def test_resolved_contact_fields(self):
        rc = SAMPLE_CONTACTS[0]
        assert rc.email == "alice@acme.com"
        assert rc.verification_status == "verified"
        assert rc.confidence == 0.95

    def test_email_draft_fields(self):
        d = SAMPLE_DRAFTS[0]
        assert d.to_email == "alice@acme.com"
        assert d.contact_name == "Alice Johnson"
        assert d.company_domain == "acme.com"

    def test_email_send_result_optional_fields(self):
        r = EmailSendResult(to_email="x@y.com", status="failed", error="timeout")
        assert r.provider_message_id is None
        assert r.error == "timeout"

    def test_stage_failure_fields(self):
        f = SAMPLE_FAILURES[0]
        assert f.stage == "eazyreach"
        assert f.item == "https://linkedin.com/in/unknown"

    def test_pipeline_run_summary_defaults(self):
        s = PipelineRunSummary(seed_domain="example.com")
        assert s.companies_found == 0
        assert s.emails_sent == 0
        assert s.run_dir == ""


# ------------------------------------------------------------------ #
# Test: JSON Storage Round-Trip
# ------------------------------------------------------------------ #

TEST_RUN_ID = "_test_run_storage"


@pytest.fixture(autouse=True)
def cleanup_test_run():
    """Remove the test run directory before and after each test."""
    test_dir = RUNS_DIR / TEST_RUN_ID
    if test_dir.exists():
        shutil.rmtree(test_dir)
    yield
    if test_dir.exists():
        shutil.rmtree(test_dir)


class TestStorage:
    """Verify JSON files are written and readable for every stage."""

    def _get_run_dir(self) -> Path:
        return create_run_dir(TEST_RUN_ID)

    def test_save_and_load_companies(self):
        run_dir = self._get_run_dir()
        save_companies(run_dir, SAMPLE_COMPANIES)
        data = load_json(run_dir, COMPANIES_FILE)
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["domain"] == "acme.com"
        assert data[0]["source"] == "ocean"
        assert data[0]["confidence"] == 0.92
        assert data[2]["confidence"] is None

    def test_save_and_load_decision_makers(self):
        run_dir = self._get_run_dir()
        save_decision_makers(run_dir, SAMPLE_DECISION_MAKERS)
        data = load_json(run_dir, DECISION_MAKERS_FILE)
        assert len(data) == 2
        assert data[0]["full_name"] == "Alice Johnson"
        assert data[1]["source"] == "prospeo"

    def test_save_and_load_resolved_contacts(self):
        run_dir = self._get_run_dir()
        save_resolved_contacts(run_dir, SAMPLE_CONTACTS)
        data = load_json(run_dir, RESOLVED_CONTACTS_FILE)
        assert len(data) == 2
        assert data[0]["email"] == "alice@acme.com"
        assert data[0]["verification_status"] == "verified"

    def test_save_and_load_email_drafts(self):
        run_dir = self._get_run_dir()
        save_email_drafts(run_dir, SAMPLE_DRAFTS)
        data = load_json(run_dir, EMAIL_DRAFTS_FILE)
        assert len(data) == 2
        assert data[0]["contact_name"] == "Alice Johnson"
        assert data[0]["company_domain"] == "acme.com"

    def test_save_and_load_send_results(self):
        run_dir = self._get_run_dir()
        save_send_results(run_dir, SAMPLE_RESULTS)
        data = load_json(run_dir, SEND_RESULTS_FILE)
        assert len(data) == 2
        assert data[0]["status"] == "sent"
        assert data[0]["provider_message_id"] == "msg-001"
        assert data[1]["provider_message_id"] is None

    def test_save_and_load_failures(self):
        run_dir = self._get_run_dir()
        save_failures(run_dir, SAMPLE_FAILURES)
        data = load_json(run_dir, FAILURES_FILE)
        assert len(data) == 1
        assert data[0]["stage"] == "eazyreach"

    def test_save_and_load_summary(self):
        run_dir = self._get_run_dir()
        summary = PipelineRunSummary(
            seed_domain="stripe.com",
            companies_found=3,
            decision_makers_found=2,
            emails_resolved=2,
            emails_ready=2,
            emails_sent=1,
            failures_count=1,
            run_dir=str(run_dir),
        )
        save_summary(run_dir, summary)
        data = load_json(run_dir, SUMMARY_FILE)
        assert data["seed_domain"] == "stripe.com"
        assert data["companies_found"] == 3
        assert data["emails_sent"] == 1
        assert data["failures_count"] == 1

    def test_full_run_creates_all_files(self):
        """Simulate a complete run: save all 7 JSON files and verify they exist."""
        run_dir = self._get_run_dir()

        save_companies(run_dir, SAMPLE_COMPANIES)
        save_decision_makers(run_dir, SAMPLE_DECISION_MAKERS)
        save_resolved_contacts(run_dir, SAMPLE_CONTACTS)
        save_email_drafts(run_dir, SAMPLE_DRAFTS)
        save_send_results(run_dir, SAMPLE_RESULTS)
        save_failures(run_dir, SAMPLE_FAILURES)
        save_summary(
            run_dir,
            PipelineRunSummary(
                seed_domain="stripe.com",
                companies_found=len(SAMPLE_COMPANIES),
                decision_makers_found=len(SAMPLE_DECISION_MAKERS),
                emails_resolved=len(SAMPLE_CONTACTS),
                emails_ready=len(SAMPLE_DRAFTS),
                emails_sent=1,
                failures_count=len(SAMPLE_FAILURES),
                run_dir=str(run_dir),
            ),
        )

        expected_files = [
            COMPANIES_FILE,
            DECISION_MAKERS_FILE,
            RESOLVED_CONTACTS_FILE,
            EMAIL_DRAFTS_FILE,
            SEND_RESULTS_FILE,
            FAILURES_FILE,
            SUMMARY_FILE,
        ]
        for filename in expected_files:
            filepath = run_dir / filename
            assert filepath.exists(), f"Missing: {filename}"
            content = json.loads(filepath.read_text(encoding="utf-8"))
            assert content is not None, f"Empty: {filename}"

    def test_load_missing_file_returns_none(self):
        run_dir = self._get_run_dir()
        assert load_json(run_dir, "nonexistent.json") is None
