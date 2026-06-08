"""
Deduplication logic for pipeline stages.
"""

from __future__ import annotations

from typing import TypeVar, Callable

from outreach import logger
from outreach.models import Company, DecisionMaker, ResolvedContact

T = TypeVar("T")


def _dedup(items: list[T], key_func: Callable[[T], str], name: str) -> list[T]:
    """Generic deduplication helper maintaining order."""
    seen = set()
    result = []
    for item in items:
        k = key_func(item)
        if k and k not in seen:
            seen.add(k)
            result.append(item)
            
    dups = len(items) - len(result)
    if dups > 0:
        logger.dim(f"Removed {dups} duplicate {name}(s)")
        
    return result


def dedup_companies(companies: list[Company]) -> list[Company]:
    return _dedup(companies, lambda c: c.domain.lower(), "company")


def dedup_decision_makers(makers: list[DecisionMaker]) -> list[DecisionMaker]:
    return _dedup(makers, lambda m: m.linkedin_url.lower(), "decision maker")


def dedup_contacts(contacts: list[ResolvedContact]) -> list[ResolvedContact]:
    return _dedup(contacts, lambda c: c.email.lower(), "contact")
