"""
Prospeo API client -- Stage 2: company domains -> decision makers.

Auth:
    Header: X-KEY
    Env var: PROSPEO_API_KEY
    Base URL: https://api.prospeo.io

Endpoint: POST /search-person (confirmed)

IMPORTANT: /search-person returns person/company data and LinkedIn-style
contact info. It does NOT return emails or mobile numbers.
Email resolution is handled by the Eazyreach stage (Stage 3).

Pagination: Use the `page` parameter to iterate through results.
"""

from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from outreach.models import DecisionMaker

# --------------------------------------------------------------------- #
# API Constants (confirmed from Prospeo docs)
# --------------------------------------------------------------------- #
BASE_URL = "https://api.prospeo.io"
SEARCH_PERSON_ENDPOINT = "/search-person"

# Seniority filters for targeting decision makers
DEFAULT_SENIORITY = ["C-level", "VP", "Director", "Manager"]


def is_retryable(exception: BaseException) -> bool:
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code == 429 or exception.response.status_code >= 500
    return isinstance(exception, httpx.RequestError)


class ProspeoClient:
    """Client for the Prospeo search-person API."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.headers = {
            "X-KEY": self.api_key,
            "Content-Type": "application/json",
        }

    def find_decision_makers(
        self,
        company_domain: str,
        limit_per_company: int = 10,
        seniority: list[str] | None = None,
    ) -> list[DecisionMaker]:
        """
        Search for decision makers for a given company domain.
        """
        if seniority is None:
            seniority = DEFAULT_SENIORITY

        persons: list[DecisionMaker] = []
        page = 1

        while len(persons) < limit_per_company:
            results = self._search_page(company_domain, seniority, page)
            if not results:
                break
            persons.extend(results)
            page += 1

        return persons[:limit_per_company]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(is_retryable),
    )
    def _search_page(
        self,
        domain: str,
        seniority: list[str],
        page: int,
    ) -> list[DecisionMaker]:
        """Fetch a single page of search-person results."""
        payload = {
            "company_domain": domain,
            "seniority": seniority,
            "page": page,
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{BASE_URL}{SEARCH_PERSON_ENDPOINT}",
                headers=self.headers,
                json=payload,
            )
            if response.status_code == 429 or response.status_code >= 500:
                response.raise_for_status()
            
            response.raise_for_status()

        data = response.json()
        persons: list[DecisionMaker] = []

        for item in data.get("results", []):
            persons.append(
                DecisionMaker(
                    company_domain=domain,
                    full_name=item.get("name", ""),
                    title=item.get("title", ""),
                    linkedin_url=item.get("linkedin_url", ""),
                    source="prospeo",
                )
            )

        return persons


# --------------------------------------------------------------------- #
# Mock Client
# --------------------------------------------------------------------- #

_MOCK_PEOPLE_POOL = [
    ("Sarah Chen", "Founder & CEO"),
    ("Michael Torres", "VP of Sales"),
    ("Priya Sharma", "Head of Growth"),
    ("James Wilson", "COO"),
    ("Elena Volkov", "CTO"),
    ("David Park", "Director of Engineering"),
    ("Rachel Adams", "VP of Marketing"),
    ("Omar Hassan", "Chief Revenue Officer"),
    ("Lena Kowalski", "Head of Partnerships"),
    ("Arjun Mehta", "VP of Product"),
    ("Clara Johansson", "Director of Sales"),
    ("Nathan Brooks", "Founder"),
]


def _make_linkedin_url(name: str) -> str:
    """Generate a plausible LinkedIn URL from a full name."""
    slug = name.lower().replace(" ", "").replace(".", "")
    return f"https://linkedin.com/in/{slug}"


class MockProspeoClient:
    """Mock Prospeo client that returns deterministic decision makers."""

    def find_decision_makers(
        self,
        company_domain: str,
        limit_per_company: int = 10,
        seniority: list[str] | None = None,
    ) -> list[DecisionMaker]:
        """Return 1-2 mock decision makers per company domain."""
        import time
        import hashlib

        time.sleep(0.3)

        persons: list[DecisionMaker] = []
        pool_len = len(_MOCK_PEOPLE_POOL)

        # Deterministic: hash domain to get a starting person index
        h = int(hashlib.sha256(company_domain.encode()).hexdigest(), 16)
        base_idx = h % pool_len

        # 1 or 2 people per company (alternate)
        # Use length of domain string to decide count so it varies
        count = 2 if len(company_domain) % 2 == 0 else 1

        for j in range(count):
            if len(persons) >= limit_per_company:
                break
            idx = (base_idx + j) % pool_len
            name, title = _MOCK_PEOPLE_POOL[idx]
            persons.append(
                DecisionMaker(
                    company_domain=company_domain,
                    full_name=name,
                    title=title,
                    linkedin_url=_make_linkedin_url(name),
                    source="prospeo",
                )
            )

        return persons

