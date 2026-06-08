"""
Pipeline orchestrator -- chains all 4 stages end-to-end.

Stages:
    1. Ocean.io    : seed domain  -> similar company domains
    2. Prospeo     : domains      -> decision makers (name, title, LinkedIn)
    3. Eazyreach   : LinkedIn URLs -> verified work emails
    4. Brevo       : verified emails -> personalized outreach sent

Hardening guarantees:
    - Domain validation before anything runs.
    - Company-domain, LinkedIn-URL and email dedup between stages.
    - Skip (not crash) on: missing LinkedIn URL, unresolved email, single
      API failure, empty API response, or partial bad data.
    - Per-item try/except so one failure never kills the whole stage.
    - Rate-limit friendly tenacity retries (429 + 5xx) in every client.
    - Final Rich summary table printed at the end of every run.
    - Clean terminal logs with stage banners, skip/dim lines, and separator.
"""

from __future__ import annotations

from pathlib import Path

from rich.prompt import Confirm
from rich.table import Table

from outreach.config import Settings
from outreach.models import PipelineRunSummary, StageFailure
from outreach.utils import generate_run_id, is_valid_domain
from outreach.dedup import dedup_companies, dedup_decision_makers, dedup_contacts
from outreach.storage import (
    create_run_dir,
    save_companies,
    save_decision_makers,
    save_resolved_contacts,
    save_email_drafts,
    save_send_results,
    save_failures,
    save_summary,
)
from outreach.email.templates import build_outreach_email
from outreach import logger

# Import mock and real clients
from outreach.stages.ocean import OceanClient, MockOceanClient
from outreach.stages.prospeo import ProspeoClient, MockProspeoClient
from outreach.stages.eazyreach import EazyreachClient, MockEazyreachClient
from outreach.stages.brevo import BrevoClient, MockBrevoClient


def run_pipeline(
    seed_domain: str,
    settings: Settings,
    mode: str = "mock",
    limit: int = 5,
    dry_run: bool = True,
    auto_confirm: bool = False,
) -> PipelineRunSummary:
    """
    Execute the full outreach pipeline.

    The pipeline is designed to *never* crash from partial failures.
    Each item is processed inside its own try/except; failures are
    recorded and the run continues with whatever data succeeded.
    """
    # ------------------------------------------------------------------ #
    # Pre-flight: validate domain
    # ------------------------------------------------------------------ #
    if not is_valid_domain(seed_domain):
        logger.error(f"Invalid domain: '{seed_domain}'. Expected format: example.com")
        bad_summary = PipelineRunSummary(seed_domain=seed_domain, run_dir="(not started)")
        logger.summary_table(bad_summary.model_dump())
        return bad_summary

    run_id = generate_run_id(seed_domain)
    run_dir = create_run_dir(run_id)

    summary = PipelineRunSummary(
        seed_domain=seed_domain,
        run_dir=run_id,
    )
    all_failures: list[StageFailure] = []

    logger.banner(
        "Outreach Pipeline",
        f"Run: {run_id}",
    )

    logger.info(f"Seed domain  : {seed_domain}")
    logger.info(f"Mode         : {mode}")
    logger.info(f"Limit        : {limit}")
    logger.info(f"Dry run      : {dry_run}")
    logger.info(f"Auto confirm : {auto_confirm}")
    logger.separator()

    # Initialize clients based on mode
    if mode == "mock":
        ocean_client = MockOceanClient()
        prospeo_client = MockProspeoClient()
        eazyreach_client = MockEazyreachClient()
        brevo_client = MockBrevoClient()
    else:
        ocean_client = OceanClient(settings.OCEAN_API_TOKEN)
        prospeo_client = ProspeoClient(settings.PROSPEO_API_KEY)
        eazyreach_client = EazyreachClient(settings.EAZYREACH_API_KEY)
        brevo_client = BrevoClient(
            api_key=settings.BREVO_API_KEY,
            sender_email=settings.BREVO_SENDER_EMAIL,
            sender_name=settings.BREVO_SENDER_NAME or settings.SENDER_NAME,
        )

    # ------------------------------------------------------------------ #
    # Stage 1: Ocean.io -- find similar companies
    # ------------------------------------------------------------------ #
    logger.stage("1/4  Ocean.io", "Finding similar companies...")

    try:
        raw_companies = ocean_client.find_similar_companies(seed_domain, limit=limit)
        # Filter out entries without a domain (bad data guard)
        raw_companies = [c for c in raw_companies if c.domain and c.domain.strip()]
        companies = dedup_companies(raw_companies)

        save_companies(run_dir, companies)
        summary.companies_found = len(companies)

        for c in companies:
            logger.dim(f"+ {c.domain} ({c.name})")

        if not companies:
            logger.warning("No similar companies found. Stopping pipeline.")
            return _finalize(summary, run_dir, all_failures)

    except Exception as e:
        logger.error(f"Stage 1 failed: {e}")
        all_failures.append(StageFailure(stage="ocean", item=seed_domain, error=str(e)))
        return _finalize(summary, run_dir, all_failures)


    # ------------------------------------------------------------------ #
    # Stage 2: Prospeo -- find decision makers
    # ------------------------------------------------------------------ #
    logger.stage("2/4  Prospeo", "Finding decision makers...")

    makers: list = []
    for c in companies:
        try:
            company_makers = prospeo_client.find_decision_makers(c.domain, limit_per_company=10)
            # Guard against None / bad return
            if company_makers:
                makers.extend(company_makers)
            else:
                logger.skip(f"No decision makers returned for {c.domain}")
        except Exception as e:
            logger.error(f"Failed to find decision makers for {c.domain}: {e}")
            all_failures.append(StageFailure(stage="prospeo", item=c.domain, error=str(e)))

    makers = dedup_decision_makers(makers)

    save_decision_makers(run_dir, makers)
    summary.decision_makers_found = len(makers)

    for m in makers:
        logger.dim(f"+ {m.full_name} ({m.title}) @ {m.company_domain}")

    if not makers:
        logger.warning("No decision makers found. Stopping pipeline.")
        return _finalize(summary, run_dir, all_failures)


    # ------------------------------------------------------------------ #
    # Stage 3: Eazyreach -- resolve verified emails
    # ------------------------------------------------------------------ #
    logger.stage("3/4  Eazyreach", "Resolving verified emails...")

    from outreach.models import ResolvedContact

    contacts: list[ResolvedContact] = []
    skipped_no_linkedin = 0

    for dm in makers:
        # --- Skip missing LinkedIn URLs (don't crash) ---
        if not dm.linkedin_url or not dm.linkedin_url.strip():
            skipped_no_linkedin += 1
            all_failures.append(StageFailure(
                stage="eazyreach",
                item=dm.full_name,
                error="No LinkedIn URL -- skipped",
            ))
            continue

        try:
            resolution = eazyreach_client.resolve_email(dm.linkedin_url)
            # --- Skip unresolved emails (don't crash) ---
            if resolution.email and resolution.email.strip():
                contacts.append(ResolvedContact(
                    company_domain=dm.company_domain,
                    full_name=dm.full_name,
                    title=dm.title,
                    linkedin_url=dm.linkedin_url,
                    email=resolution.email,
                    verification_status=resolution.verification_status,
                    confidence=resolution.confidence,
                ))
            else:
                logger.skip(f"Unresolved email for {dm.full_name}: {resolution.error or 'empty'}")
                all_failures.append(StageFailure(
                    stage="eazyreach",
                    item=dm.linkedin_url,
                    error=resolution.error or "Could not resolve email",
                ))
        except Exception as e:
            logger.error(f"Email resolution error for {dm.full_name}: {e}")
            all_failures.append(StageFailure(
                stage="eazyreach",
                item=dm.linkedin_url,
                error=str(e),
            ))

    if skipped_no_linkedin:
        logger.skip(f"{skipped_no_linkedin} decision maker(s) had no LinkedIn URL")

    contacts = dedup_contacts(contacts)

    save_resolved_contacts(run_dir, contacts)
    summary.emails_resolved = len(contacts)

    for c in contacts:
        logger.dim(f"+ {c.email} (Confidence: {c.confidence or 'N/A'})")

    if not contacts:
        logger.warning("No verified emails resolved. Stopping pipeline.")
        return _finalize(summary, run_dir, all_failures)


    # ------------------------------------------------------------------ #
    # Email Draft Generation
    # ------------------------------------------------------------------ #
    logger.stage("Generate", "Creating personalized email drafts...")

    drafts = []
    for contact in contacts:
        try:
            drafts.append(
                build_outreach_email(contact=contact, seed_domain=seed_domain, settings=settings)
            )
        except Exception as e:
            logger.error(f"Draft generation failed for {contact.email}: {e}")
            all_failures.append(StageFailure(stage="draft", item=contact.email, error=str(e)))

    save_email_drafts(run_dir, drafts)
    summary.emails_ready = len(drafts)

    logger.info(f"Generated {len(drafts)} draft(s).")


    # ------------------------------------------------------------------ #
    # Safety Checkpoint
    # ------------------------------------------------------------------ #
    if dry_run:
        logger.separator()
        logger.info("DRY RUN enabled. Stopping before sending.")
        return _finalize(summary, run_dir, all_failures)

    logger.separator()
    logger.warning("SAFETY CHECKPOINT")

    table = Table(show_lines=True)
    table.add_column("Recipient")
    table.add_column("Company")
    table.add_column("Subject")
    for d in drafts:
        table.add_row(d.to_email, d.company_domain, d.subject)

    logger.console.print(table)

    proceed = False
    if mode == "mock" and auto_confirm:
        logger.info("Auto-confirming safety checkpoint (--yes passed).")
        proceed = True
    else:
        proceed = Confirm.ask("Proceed with sending these emails?")

    if not proceed:
        logger.info("Sending aborted by user.")
        return _finalize(summary, run_dir, all_failures)


    # ------------------------------------------------------------------ #
    # Stage 4: Brevo -- send outreach emails
    # ------------------------------------------------------------------ #
    logger.stage("4/4  Brevo", "Sending outreach emails...")

    from outreach.models import EmailSendResult

    results: list[EmailSendResult] = []
    for draft in drafts:
        try:
            result = brevo_client.send_email(draft)
            results.append(result)
        except Exception as e:
            results.append(EmailSendResult(
                to_email=draft.to_email,
                status="failed",
                error=str(e),
            ))

    save_send_results(run_dir, results)

    sent_count = 0
    for r in results:
        if r.status == "sent":
            sent_count += 1
            logger.dim(f"Sent -> {r.to_email} (Msg ID: {r.provider_message_id})")
        else:
            logger.error(f"Failed -> {r.to_email}: {r.error}")
            all_failures.append(StageFailure(stage="brevo", item=r.to_email, error=r.error or "Unknown error"))

    summary.emails_sent = sent_count


    # ------------------------------------------------------------------ #
    # Finalize
    # ------------------------------------------------------------------ #
    return _finalize(summary, run_dir, all_failures)


def _finalize(
    summary: PipelineRunSummary,
    run_dir: Path,
    all_failures: list[StageFailure],
) -> PipelineRunSummary:
    """Save final failures, send_results (if missing), and summary.

    Guarantees that failures.json, send_results.json, and summary.json
    always exist in the run directory regardless of how far the pipeline got.
    """
    summary.failures_count = len(all_failures)

    # Always write failures.json (empty list when no failures)
    save_failures(run_dir, all_failures)

    # Always write send_results.json (empty list when stage 4 was not reached)
    send_results_path = run_dir / "send_results.json"
    if not send_results_path.exists():
        save_send_results(run_dir, [])

    # Always write summary.json
    save_summary(run_dir, summary)

    logger.separator()
    logger.success(f"Pipeline completed: {summary.run_dir}")

    # Final summary table (the acceptance-criteria table)
    logger.summary_table(summary.model_dump())

    return summary
