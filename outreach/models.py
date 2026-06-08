"""
Typed data models for every stage of the outreach pipeline.

Stage 1 (Ocean.io)   -> Company
Stage 2 (Prospeo)    -> DecisionMaker  (LinkedIn data only, no email)
Stage 3 (Eazyreach)  -> ResolvedContact  (verified email from LinkedIn URL)
Stage 4 (Brevo)      -> EmailDraft, EmailSendResult

Cross-cutting         -> StageFailure
Metadata              -> PipelineRunSummary
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ------------------------------------------------------------------ #
# Stage 1: Similar Companies (Ocean.io)
# ------------------------------------------------------------------ #

class Company(BaseModel):
    """A company discovered via Ocean.io lookalike search."""
    domain: str
    name: str = ""
    source: str = "ocean"
    confidence: Optional[float] = None


# ------------------------------------------------------------------ #
# Stage 2: Decision Makers (Prospeo)
# ------------------------------------------------------------------ #

class DecisionMaker(BaseModel):
    """
    A decision maker found via Prospeo /search-person.

    NOTE: Prospeo search-person returns person/company data and LinkedIn
    contact info. It does NOT return emails or mobile numbers.
    Email resolution is handled by the Eazyreach stage (Stage 3).
    """
    company_domain: str
    full_name: str
    title: str = ""
    linkedin_url: str = ""
    source: str = "prospeo"


# ------------------------------------------------------------------ #
# Stage 3: Resolved Contacts (Eazyreach)
# ------------------------------------------------------------------ #

class ResolvedContact(BaseModel):
    """A contact with a verified work email, resolved by Eazyreach."""
    company_domain: str
    full_name: str
    title: str = ""
    linkedin_url: str = ""
    email: str = ""
    verification_status: str = ""  # e.g. "verified", "unverified", "risky"
    confidence: Optional[float] = None  # 0.0 to 1.0


# ------------------------------------------------------------------ #
# Stage 4: Email Drafts & Send Results (Brevo)
# ------------------------------------------------------------------ #

class EmailResolution(BaseModel):
    """
    Lightweight resolution result from Stage 3 (Eazyreach).
    This will be merged with a DecisionMaker to form a ResolvedContact.
    """
    email: str | None = None
    verification_status: str
    confidence: float | None = None
    error: str | None = None


class EmailDraft(BaseModel):
    """A personalized email ready to be sent via Brevo."""
    to_email: str
    subject: str = ""
    body: str = ""
    contact_name: str = ""
    company_domain: str = ""


class EmailSendResult(BaseModel):
    """Result of attempting to send one outreach email via Brevo."""
    to_email: str
    status: str = ""  # "sent", "failed", "skipped", "dry_run"
    provider_message_id: Optional[str] = None
    error: Optional[str] = None


# ------------------------------------------------------------------ #
# Cross-cutting: Stage Failures
# ------------------------------------------------------------------ #

class StageFailure(BaseModel):
    """A failure that occurred during a pipeline stage."""
    stage: str  # "ocean", "prospeo", "eazyreach", "brevo"
    item: str  # the input that caused the failure (domain, URL, email, etc.)
    error: str


# ------------------------------------------------------------------ #
# Run Summary
# ------------------------------------------------------------------ #

class PipelineRunSummary(BaseModel):
    """Top-level metadata and statistics for a single pipeline run."""
    seed_domain: str
    companies_found: int = 0
    decision_makers_found: int = 0
    emails_resolved: int = 0
    emails_ready: int = 0
    emails_sent: int = 0
    failures_count: int = 0
    run_dir: str = ""
