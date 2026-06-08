"""
Ocean.io API client -- Stage 1: seed domain -> similar companies.

Auth:
    Header: X-Api-Token
    Env var: OCEAN_API_TOKEN

TODO: Confirm exact endpoint path and request payload from Ocean.io
      account dashboard or API docs at https://api.ocean.io/v2/docs.
"""

from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from outreach.models import Company

# --------------------------------------------------------------------- #
# API Constants
# TODO: Confirm exact endpoint path from Ocean.io account/docs.
# Suspected: POST /v2/companies/lookalike -- UNVERIFIED, update from docs.
# --------------------------------------------------------------------- #
BASE_URL = "https://api.ocean.io"
OCEAN_ENDPOINT = "/v2/companies/lookalike"  # UNVERIFIED -- update from docs

# TODO: Confirm exact request payload schema.
# Suspected fields: domains (list[str]), size (int)


def is_retryable(exception: BaseException) -> bool:
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code == 429 or exception.response.status_code >= 500
    return isinstance(exception, httpx.RequestError)


class OceanClient:
    """Client for the Ocean.io lookalike companies API."""

    def __init__(self, api_token: str) -> None:
        self.api_token = api_token
        self.headers = {
            "X-Api-Token": self.api_token,
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(is_retryable),
    )
    def find_similar_companies(
        self,
        seed_domain: str,
        limit: int = 5,
    ) -> list[Company]:
        """
        Find companies similar to the seed domain.

        Args:
            seed_domain: The company domain to find lookalikes for.
            limit: Maximum number of results to return.

        Returns:
            List of Company models.

        Raises:
            httpx.HTTPStatusError: On non-2xx responses.
            httpx.RequestError: On network errors.
        """
        payload = {
            "domains": [seed_domain],
            "size": limit,
        }

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{BASE_URL}{OCEAN_ENDPOINT}",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()

        # TODO: Update response parsing once actual schema is confirmed.
        data = response.json()
        companies: list[Company] = []
        for item in data.get("results", []):
            companies.append(
                Company(
                    domain=item.get("domain", ""),
                    name=item.get("name", ""),
                    source="ocean",
                    confidence=item.get("similarity_score"),
                )
            )
        return companies[:limit]


# --------------------------------------------------------------------- #
# Mock Client
# --------------------------------------------------------------------- #

# Realistic SaaS-style companies for mock mode
_MOCK_COMPANY_POOL = [
    ("techflow.io", "TechFlow", 0.94),
    ("cloudnova.com", "CloudNova", 0.91),
    ("databridge.ai", "DataBridge AI", 0.88),
    ("scaleops.dev", "ScaleOps", 0.85),
    ("nextera.io", "Nextera Systems", 0.83),
    ("pulsemetrics.com", "PulseMetrics", 0.80),
    ("vantagepoint.io", "Vantage Point", 0.78),
    ("synthwave.dev", "Synthwave Labs", 0.75),
    ("gridline.co", "Gridline Analytics", 0.72),
    ("horizonhq.com", "Horizon HQ", 0.70),
]


class MockOceanClient:
    """Mock Ocean.io client that returns deterministic sample companies."""

    def find_similar_companies(
        self,
        seed_domain: str,
        limit: int = 5,
    ) -> list[Company]:
        """Return mock similar companies, deterministically seeded by domain."""
        import time
        import hashlib

        # Small delay to simulate API call
        time.sleep(0.3)

        # Deterministic shuffle: hash the seed domain to pick a starting offset
        h = int(hashlib.sha256(seed_domain.encode()).hexdigest(), 16)
        offset = h % len(_MOCK_COMPANY_POOL)

        companies: list[Company] = []
        for i in range(min(limit, len(_MOCK_COMPANY_POOL))):
            idx = (offset + i) % len(_MOCK_COMPANY_POOL)
            domain, name, score = _MOCK_COMPANY_POOL[idx]
            companies.append(
                Company(
                    domain=domain,
                    name=name,
                    source="ocean",
                    confidence=score,
                )
            )

        return companies

