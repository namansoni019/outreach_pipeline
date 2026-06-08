"""
Shared utility functions for the outreach pipeline.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone


def generate_run_id(seed_domain: str) -> str:
    """
    Generate a unique run ID in the format YYYYMMDD-HHMMSS-domain.

    Example: 20260606-093300-stripe.com
    """
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    # Sanitize domain for filesystem safety
    safe_domain = seed_domain.replace("/", "_").replace("\\", "_").strip(".")
    return f"{timestamp}-{safe_domain}"


def now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


# Regex: at least one label with alphanumeric + hyphens, a dot, then a 2-63 char TLD
_DOMAIN_RE = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"  # labels
    r"[a-z]{2,63}$",                                    # TLD
    re.IGNORECASE,
)


def is_valid_domain(domain: str) -> bool:
    """
    Return True if *domain* looks like a plausible internet domain.

    Accepts bare domains only (no protocol, no path, no port).
    """
    if not domain or len(domain) > 253:
        return False
    return _DOMAIN_RE.match(domain) is not None


def sanitize_domain(domain: str) -> str:
    """
    Clean a domain input: strip protocol, trailing slashes, whitespace.

    Examples:
        https://www.stripe.com/ -> stripe.com
        WWW.EXAMPLE.COM -> example.com
    """
    domain = domain.strip().lower()
    for prefix in ("https://", "http://", "www."):
        if domain.startswith(prefix):
            domain = domain[len(prefix):]
    return domain.rstrip("/").strip()


def short_hash(value: str, length: int = 8) -> str:
    """Return a short hex hash of a string (for dedup keys, etc.)."""
    return hashlib.sha256(value.encode()).hexdigest()[:length]
