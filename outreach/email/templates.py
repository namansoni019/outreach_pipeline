"""
Email templates for personalized outreach.
"""

from __future__ import annotations

import re

from outreach.models import ResolvedContact, EmailDraft
from outreach.config import Settings


def _extract_title_area(title: str) -> str:
    """Extract a broad area from a specific job title. E.g., 'VP of Sales' -> 'sales'."""
    title = title.lower()
    if not title:
        return "operations"
        
    for area in ["sales", "marketing", "engineering", "product", "growth", "revenue", "partnerships"]:
        if area in title:
            return area
            
    if "ceo" in title or "founder" in title or "coo" in title:
        return "operations"
        
    return "operations"


def build_outreach_email(
    contact: ResolvedContact, 
    seed_domain: str, 
    settings: Settings
) -> EmailDraft:
    """
    Generate a professional, personalized outreach email.
    
    Args:
        contact: The resolved contact to email.
        seed_domain: The original seed domain that started the pipeline.
        settings: Application settings containing sender info.
        
    Returns:
        A populated EmailDraft.
    """
    # Extract first name for a friendlier greeting
    first_name = contact.full_name.split()[0] if contact.full_name else "there"
    
    # Extract area from title
    title_area = _extract_title_area(contact.title)
    
    company = contact.company_domain
    
    subject = f"Quick idea for {company}"
    
    body = f"""\
Hi {first_name},

I noticed you lead {title_area} at {company}. I'm working on a lightweight automation that helps teams identify high-intent companies and reach the right decision-makers with less manual research.

Would it be unreasonable to share a 2-minute overview this week?

Best,
{settings.SENDER_NAME}
{settings.SENDER_COMPANY}
"""

    return EmailDraft(
        to_email=contact.email,
        subject=subject,
        body=body,
        contact_name=contact.full_name,
        company_domain=contact.company_domain,
    )
