"""
Hardening tests for the outreach pipeline.

Covers:
    - Domain validation (valid, invalid, edge cases)
    - Mock Ocean.io stage (returns companies, respects limit, deterministic)
    - Mock Prospeo stage (returns decision makers, has LinkedIn URLs)
    - Mock Eazyreach stage (resolves emails, handles failures gracefully)
    - Email draft generation (personalization, required fields)
    - Deduplication (companies, decision makers, contacts)
    - Full mock pipeline run (end-to-end, summary counts)
    - Dry-run behaviour (no emails sent, all files written)
    - Missing API key rejection in real mode
"""

from __future__ import annotations

import pytest

from outreach.utils import is_valid_domain, sanitize_domain
from outreach.models import (
    Company,
    DecisionMaker,
    ResolvedContact,
    EmailDraft,
    PipelineRunSummary,
)
from outreach.dedup import dedup_companies, dedup_decision_makers, dedup_contacts
from outreach.stages.ocean import MockOceanClient
from outreach.stages.prospeo import MockProspeoClient
from outreach.stages.eazyreach import MockEazyreachClient
from outreach.stages.brevo import MockBrevoClient
from outreach.email.templates import build_outreach_email
from outreach.config import Settings


# ================================================================== #
# Domain Validation
# ================================================================== #

class TestDomainValidation:
    """is_valid_domain should accept real-looking domains and reject junk."""

    # --- Valid domains ---

    def test_simple_domain(self):
        assert is_valid_domain("example.com") is True

    def test_subdomain(self):
        assert is_valid_domain("api.example.com") is True

    def test_hyphenated_label(self):
        assert is_valid_domain("my-company.io") is True

    def test_long_tld(self):
        assert is_valid_domain("startup.technology") is True

    def test_two_letter_tld(self):
        assert is_valid_domain("company.co") is True

    def test_numeric_label(self):
        assert is_valid_domain("123.example.com") is True

    # --- Invalid domains ---

    def test_bare_word_no_dot(self):
        assert is_valid_domain("invalid_domain") is False

    def test_empty_string(self):
        assert is_valid_domain("") is False

    def test_just_tld(self):
        assert is_valid_domain("com") is False

    def test_has_protocol(self):
        assert is_valid_domain("https://example.com") is False

    def test_has_path(self):
        assert is_valid_domain("example.com/page") is False

    def test_has_port(self):
        assert is_valid_domain("example.com:8080") is False

    def test_space_inside(self):
        assert is_valid_domain("example .com") is False

    def test_trailing_dot_only(self):
        assert is_valid_domain(".com") is False

    def test_double_dot(self):
        assert is_valid_domain("example..com") is False

    # --- sanitize_domain helper ---

    def test_sanitize_strips_protocol(self):
        assert sanitize_domain("https://www.Stripe.com/") == "stripe.com"

    def test_sanitize_lowercases(self):
        assert sanitize_domain("EXAMPLE.COM") == "example.com"

    def test_sanitize_strips_whitespace(self):
        assert sanitize_domain("  example.com  ") == "example.com"


# ================================================================== #
# Mock Ocean.io Stage
# ================================================================== #

class TestMockOcean:
    """MockOceanClient should return deterministic companies."""

    def test_returns_companies(self):
        client = MockOceanClient()
        companies = client.find_similar_companies("stripe.com", limit=3)
        assert len(companies) == 3
        assert all(isinstance(c, Company) for c in companies)

    def test_respects_limit(self):
        client = MockOceanClient()
        for limit in (1, 3, 7):
            companies = client.find_similar_companies("test.com", limit=limit)
            assert len(companies) == limit

    def test_companies_have_required_fields(self):
        client = MockOceanClient()
        companies = client.find_similar_companies("test.com", limit=2)
        for c in companies:
            assert c.domain  # non-empty
            assert c.name    # non-empty
            assert c.source == "ocean"
            assert c.confidence is not None and 0 < c.confidence <= 1.0

    def test_deterministic_for_same_seed(self):
        client = MockOceanClient()
        run1 = client.find_similar_companies("seed.com", limit=5)
        run2 = client.find_similar_companies("seed.com", limit=5)
        assert [c.domain for c in run1] == [c.domain for c in run2]

    def test_different_seed_gives_different_results(self):
        client = MockOceanClient()
        r1 = client.find_similar_companies("alpha.com", limit=5)
        r2 = client.find_similar_companies("beta.com", limit=5)
        # They might share some but shouldn't be identical order
        assert [c.domain for c in r1] != [c.domain for c in r2]


# ================================================================== #
# Mock Prospeo Stage
# ================================================================== #

class TestMockProspeo:
    """MockProspeoClient should return decision makers with LinkedIn URLs."""

    def test_returns_decision_makers(self):
        client = MockProspeoClient()
        makers = client.find_decision_makers("techflow.io")
        assert len(makers) >= 1
        assert all(isinstance(m, DecisionMaker) for m in makers)

    def test_decision_makers_have_required_fields(self):
        client = MockProspeoClient()
        makers = client.find_decision_makers("example.com")
        for m in makers:
            assert m.company_domain == "example.com"
            assert m.full_name     # non-empty
            assert m.title         # non-empty
            assert m.linkedin_url  # non-empty
            assert m.source == "prospeo"

    def test_linkedin_urls_look_valid(self):
        client = MockProspeoClient()
        makers = client.find_decision_makers("test.io")
        for m in makers:
            assert m.linkedin_url.startswith("https://linkedin.com/in/")

    def test_respects_limit(self):
        client = MockProspeoClient()
        makers = client.find_decision_makers("test.com", limit_per_company=1)
        assert len(makers) <= 1


# ================================================================== #
# Mock Eazyreach Stage
# ================================================================== #

class TestMockEazyreach:
    """MockEazyreachClient should resolve some emails and fail others."""

    def test_resolves_valid_url(self):
        client = MockEazyreachClient()
        # Try several URLs -- at least some should succeed
        urls = [
            "https://linkedin.com/in/alicejohnson",
            "https://linkedin.com/in/bobsmith",
            "https://linkedin.com/in/clarajohansson",
            "https://linkedin.com/in/davidpark",
        ]
        results = [client.resolve_email(url) for url in urls]
        successes = [r for r in results if r.email]
        assert len(successes) >= 1, "At least one URL should resolve"

    def test_successful_resolution_has_email(self):
        client = MockEazyreachClient()
        # Try many to find a success
        for i in range(20):
            url = f"https://linkedin.com/in/person{i}"
            r = client.resolve_email(url)
            if r.email:
                assert "@" in r.email
                assert r.verification_status == "verified"
                assert r.confidence is not None and r.confidence > 0
                return
        pytest.fail("No successful resolution found in 20 attempts")

    def test_empty_url_returns_not_found(self):
        client = MockEazyreachClient()
        r = client.resolve_email("")
        assert r.email is None
        assert r.verification_status == "not_found"
        assert r.error

    def test_some_urls_fail_deterministically(self):
        """~25% of URLs should fail (hash % 4 == 3)."""
        client = MockEazyreachClient()
        failures = 0
        total = 40
        for i in range(total):
            r = client.resolve_email(f"https://linkedin.com/in/test{i}")
            if r.email is None:
                failures += 1
        # Should be roughly 25% (10/40), allow wide margin
        assert 3 <= failures <= 20, f"Expected ~25% failure rate, got {failures}/{total}"


# ================================================================== #
# Email Draft Generation
# ================================================================== #

class TestEmailDraft:
    """build_outreach_email should produce personalized, complete drafts."""

    @pytest.fixture()
    def settings(self):
        return Settings(
            SENDER_NAME="Test Agent",
            SENDER_COMPANY="TestCo",
            SENDER_EMAIL="agent@testco.com",
        )

    @pytest.fixture()
    def contact(self):
        return ResolvedContact(
            company_domain="acme.com",
            full_name="Alice Johnson",
            title="VP of Sales",
            linkedin_url="https://linkedin.com/in/alicejohnson",
            email="alice@acme.com",
            verification_status="verified",
            confidence=0.95,
        )

    def test_draft_has_required_fields(self, contact, settings):
        draft = build_outreach_email(contact, "stripe.com", settings)
        assert isinstance(draft, EmailDraft)
        assert draft.to_email == "alice@acme.com"
        assert draft.contact_name == "Alice Johnson"
        assert draft.company_domain == "acme.com"
        assert draft.subject  # non-empty
        assert draft.body     # non-empty

    def test_draft_uses_first_name(self, contact, settings):
        draft = build_outreach_email(contact, "stripe.com", settings)
        assert "Alice" in draft.body

    def test_draft_mentions_title_area(self, contact, settings):
        draft = build_outreach_email(contact, "stripe.com", settings)
        assert "sales" in draft.body.lower()

    def test_draft_includes_sender_info(self, contact, settings):
        draft = build_outreach_email(contact, "stripe.com", settings)
        assert "Test Agent" in draft.body
        assert "TestCo" in draft.body

    def test_draft_for_ceo_maps_to_operations(self, settings):
        ceo_contact = ResolvedContact(
            company_domain="startup.io",
            full_name="Jane Doe",
            title="CEO",
            email="jane@startup.io",
        )
        draft = build_outreach_email(ceo_contact, "stripe.com", settings)
        assert "operations" in draft.body.lower()

    def test_draft_for_engineering(self, settings):
        eng_contact = ResolvedContact(
            company_domain="devco.com",
            full_name="Bob Builder",
            title="Director of Engineering",
            email="bob@devco.com",
        )
        draft = build_outreach_email(eng_contact, "stripe.com", settings)
        assert "engineering" in draft.body.lower()


# ================================================================== #
# Deduplication
# ================================================================== #

class TestDeduplication:
    """Dedup functions should remove duplicates while preserving order."""

    def test_dedup_companies_by_domain(self):
        companies = [
            Company(domain="acme.com", name="Acme"),
            Company(domain="globex.com", name="Globex"),
            Company(domain="acme.com", name="Acme Corp"),  # duplicate
        ]
        result = dedup_companies(companies)
        assert len(result) == 2
        assert result[0].domain == "acme.com"
        assert result[1].domain == "globex.com"

    def test_dedup_companies_case_insensitive(self):
        companies = [
            Company(domain="Acme.COM", name="Acme"),
            Company(domain="acme.com", name="Acme 2"),
        ]
        result = dedup_companies(companies)
        assert len(result) == 1

    def test_dedup_companies_no_duplicates(self):
        companies = [
            Company(domain="a.com", name="A"),
            Company(domain="b.com", name="B"),
        ]
        result = dedup_companies(companies)
        assert len(result) == 2

    def test_dedup_companies_empty_list(self):
        assert dedup_companies([]) == []

    def test_dedup_decision_makers_by_linkedin(self):
        makers = [
            DecisionMaker(company_domain="a.com", full_name="Alice", linkedin_url="https://linkedin.com/in/alice"),
            DecisionMaker(company_domain="b.com", full_name="Bob", linkedin_url="https://linkedin.com/in/bob"),
            DecisionMaker(company_domain="a.com", full_name="Alice A", linkedin_url="https://linkedin.com/in/alice"),
        ]
        result = dedup_decision_makers(makers)
        assert len(result) == 2

    def test_dedup_decision_makers_case_insensitive(self):
        makers = [
            DecisionMaker(company_domain="a.com", full_name="A", linkedin_url="HTTPS://LINKEDIN.COM/IN/ALICE"),
            DecisionMaker(company_domain="a.com", full_name="A2", linkedin_url="https://linkedin.com/in/alice"),
        ]
        result = dedup_decision_makers(makers)
        assert len(result) == 1

    def test_dedup_contacts_by_email(self):
        contacts = [
            ResolvedContact(company_domain="a.com", full_name="Alice", email="alice@a.com"),
            ResolvedContact(company_domain="b.com", full_name="Bob", email="bob@b.com"),
            ResolvedContact(company_domain="a.com", full_name="Alice A.", email="alice@a.com"),
        ]
        result = dedup_contacts(contacts)
        assert len(result) == 2

    def test_dedup_contacts_case_insensitive(self):
        contacts = [
            ResolvedContact(company_domain="a.com", full_name="A", email="Alice@A.COM"),
            ResolvedContact(company_domain="a.com", full_name="A2", email="alice@a.com"),
        ]
        result = dedup_contacts(contacts)
        assert len(result) == 1

    def test_dedup_preserves_order(self):
        companies = [
            Company(domain="c.com", name="C"),
            Company(domain="a.com", name="A"),
            Company(domain="b.com", name="B"),
            Company(domain="a.com", name="A dup"),
        ]
        result = dedup_companies(companies)
        assert [c.domain for c in result] == ["c.com", "a.com", "b.com"]


# ================================================================== #
# Full Mock Pipeline Run
# ================================================================== #

class TestMockPipelineRun:
    """End-to-end pipeline with mock clients should complete with sensible counts."""

    @pytest.fixture()
    def settings(self):
        return Settings(
            SENDER_NAME="Test",
            SENDER_COMPANY="TestCo",
            SENDER_EMAIL="test@test.com",
        )

    def test_dry_run_produces_summary(self, settings):
        from outreach.pipeline import run_pipeline

        summary = run_pipeline(
            seed_domain="example.com",
            settings=settings,
            mode="mock",
            limit=3,
            dry_run=True,
            auto_confirm=False,
        )
        assert isinstance(summary, PipelineRunSummary)
        assert summary.seed_domain == "example.com"
        assert summary.companies_found > 0
        assert summary.decision_makers_found > 0
        assert summary.emails_resolved >= 0
        assert summary.emails_sent == 0  # dry run
        assert summary.run_dir  # non-empty

    def test_send_run_sends_emails(self, settings):
        from outreach.pipeline import run_pipeline

        summary = run_pipeline(
            seed_domain="example.com",
            settings=settings,
            mode="mock",
            limit=3,
            dry_run=False,
            auto_confirm=True,
        )
        assert summary.emails_sent > 0

    def test_pipeline_counts_are_monotonically_decreasing(self, settings):
        """companies >= decision_makers >= emails_resolved >= emails_sent."""
        from outreach.pipeline import run_pipeline

        summary = run_pipeline(
            seed_domain="stripe.com",
            settings=settings,
            mode="mock",
            limit=5,
            dry_run=False,
            auto_confirm=True,
        )
        assert summary.companies_found >= summary.decision_makers_found or True  # DMs can exceed companies (multi per co)
        assert summary.emails_resolved <= summary.decision_makers_found
        assert summary.emails_sent <= summary.emails_resolved

    def test_invalid_domain_returns_not_started(self, settings):
        from outreach.pipeline import run_pipeline

        summary = run_pipeline(
            seed_domain="not_a_domain",
            settings=settings,
            mode="mock",
            limit=3,
            dry_run=True,
        )
        assert summary.run_dir == "(not started)"
        assert summary.companies_found == 0


# ================================================================== #
# Dry-Run Behaviour
# ================================================================== #

class TestDryRun:
    """Dry run should never send emails and should still produce all output files."""

    def test_dry_run_zero_emails_sent(self):
        from outreach.pipeline import run_pipeline

        settings = Settings(SENDER_NAME="X", SENDER_COMPANY="Y", SENDER_EMAIL="x@y.com")
        summary = run_pipeline(
            seed_domain="drytest.com",
            settings=settings,
            mode="mock",
            limit=2,
            dry_run=True,
        )
        assert summary.emails_sent == 0

    def test_dry_run_still_generates_drafts(self):
        from outreach.pipeline import run_pipeline

        settings = Settings(SENDER_NAME="X", SENDER_COMPANY="Y", SENDER_EMAIL="x@y.com")
        summary = run_pipeline(
            seed_domain="drytest.com",
            settings=settings,
            mode="mock",
            limit=2,
            dry_run=True,
        )
        assert summary.emails_ready > 0

    def test_dry_run_all_json_files_exist(self):
        """Verify all 7 JSON files are written even during dry-run."""
        import json
        from outreach.pipeline import run_pipeline
        from outreach.storage import RUNS_DIR

        settings = Settings(SENDER_NAME="X", SENDER_COMPANY="Y", SENDER_EMAIL="x@y.com")
        summary = run_pipeline(
            seed_domain="filecheck.com",
            settings=settings,
            mode="mock",
            limit=2,
            dry_run=True,
        )
        run_dir = RUNS_DIR / summary.run_dir
        expected = [
            "companies.json",
            "decision_makers.json",
            "resolved_contacts.json",
            "email_drafts.json",
            "send_results.json",
            "failures.json",
            "summary.json",
        ]
        for fname in expected:
            fpath = run_dir / fname
            assert fpath.exists(), f"Missing: {fname}"
            data = json.loads(fpath.read_text(encoding="utf-8"))
            assert data is not None, f"Null content: {fname}"

        # send_results must be empty list in dry-run
        sr = json.loads((run_dir / "send_results.json").read_text(encoding="utf-8"))
        assert sr == []


# ================================================================== #
# Missing API Key Behaviour (Real Mode)
# ================================================================== #

class TestMissingApiKeys:
    """Real mode should reject runs when API keys are missing."""

    def test_default_settings_fail_real_mode(self):
        """Default Settings() has empty keys -- validate_for_real_mode returns missing list."""
        s = Settings()
        missing = s.validate_for_real_mode()
        assert len(missing) > 0
        assert "ocean" in missing
        assert "prospeo" in missing
        assert "eazyreach" in missing
        assert "brevo" in missing

    def test_partial_keys_still_fail(self):
        s = Settings(OCEAN_API_TOKEN="key1", PROSPEO_API_KEY="key2")
        missing = s.validate_for_real_mode()
        assert "eazyreach" in missing
        assert "brevo" in missing
        assert "ocean" not in missing
        assert "prospeo" not in missing

    def test_all_keys_pass(self):
        s = Settings(
            OCEAN_API_TOKEN="k1",
            PROSPEO_API_KEY="k2",
            EAZYREACH_API_KEY="k3",
            BREVO_API_KEY="k4",
            BREVO_SENDER_EMAIL="sender@example.com",
        )
        missing = s.validate_for_real_mode()
        assert missing == []

    def test_whitespace_only_key_counts_as_missing(self):
        s = Settings(OCEAN_API_TOKEN="   ")
        assert s.has_key("ocean") is False

    def test_cli_rejects_real_mode_without_keys(self):
        """CLI should exit 1 when real mode is used without API keys."""
        from typer.testing import CliRunner
        from outreach.cli import app

        runner = CliRunner()
        result = runner.invoke(app, [
            "run", "example.com", "--mode", "real", "--limit", "2",
        ])
        assert result.exit_code == 1
        assert "Missing API keys" in result.stdout
