"""
Eazyreach API client -- Stage 3: LinkedIn URLs -> verified work emails.

Auth:
    Env var: EAZYREACH_API_KEY
    Auth header: TBD (see docs.eazyreach.app for API Keys/Webhooks section)

TODO: Confirm exact endpoint, auth header name, and payload schema from
      docs.eazyreach.app or your Eazyreach account dashboard.
"""

from __future__ import annotations

import httpx

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from outreach.models import EmailResolution


# --------------------------------------------------------------------- #
# API Constants
# TODO: Confirm exact endpoint and auth header from docs.eazyreach.app.
#       The API Keys/Webhooks section in their docs describes authentication.
# --------------------------------------------------------------------- #
BASE_URL = "https://api.eazyreach.app"
EAZYREACH_ENDPOINT = "/v1/email-finder"  # UNVERIFIED -- update from docs

# TODO: Confirm the auth header name. Common patterns:
#   "Authorization": "Bearer {key}"
#   "X-API-Key": "{key}"
#   "api-key": "{key}"
AUTH_HEADER_NAME = "Authorization"  # UNVERIFIED -- update from docs


def is_retryable(exception: BaseException) -> bool:
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code == 429 or exception.response.status_code >= 500
    return isinstance(exception, httpx.RequestError)


class EazyreachClient:
    """Client for the Eazyreach email finder API."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.headers = {
            AUTH_HEADER_NAME: f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(is_retryable),
    )
    def resolve_email(self, linkedin_url: str) -> EmailResolution:
        """
        Resolve a single LinkedIn URL to a verified email.
        """
        # TODO: Update payload structure once confirmed from docs.
        payload = {
            "linkedin_url": linkedin_url,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{BASE_URL}{EAZYREACH_ENDPOINT}",
                    headers=self.headers,
                    json=payload,
                )
                if response.status_code == 429 or response.status_code >= 500:
                    response.raise_for_status()
                
                response.raise_for_status()

            # TODO: Update response parsing once actual schema is confirmed.
            data = response.json()
            email = data.get("email", "")
            if not email:
                return EmailResolution(
                    email=None,
                    verification_status="not_found",
                    error="No email returned by API"
                )

            return EmailResolution(
                email=email,
                verification_status=data.get("verification_status", "verified"),
                confidence=data.get("confidence"),
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return EmailResolution(
                    email=None,
                    verification_status="not_found",
                    error="Contact not found"
                )
            raise


# --------------------------------------------------------------------- #
# Mock Client
# --------------------------------------------------------------------- #

class MockEazyreachClient:
    """
    Mock Eazyreach client that resolves most contacts successfully,
    marks some as not_found or unverifiable to test graceful handling.
    """

    def resolve_email(self, linkedin_url: str) -> EmailResolution:
        """
        Mock email resolution. Deterministic based on hash of URL.
        """
        import time
        import hashlib
        
        time.sleep(0.1)

        if not linkedin_url:
            return EmailResolution(email=None, verification_status="not_found", error="No LinkedIn URL provided")

        # Deterministic failure logic
        h = int(hashlib.sha256(linkedin_url.encode()).hexdigest(), 16)
        
        # ~25% fail
        if h % 4 == 3:
            status = "not_found" if h % 2 == 0 else "unverifiable"
            return EmailResolution(
                email=None,
                verification_status=status,
                error=f"Email resolution failed: {status}"
            )

        # Generate mock email from the slug
        # URL looks like https://linkedin.com/in/firstlast
        slug = linkedin_url.split("/")[-1]
        
        # Fake a domain since we don't have company domain here
        mock_domain = "company.com"
        
        return EmailResolution(
            email=f"{slug}@{mock_domain}", # The pipeline merges real domain later
            verification_status="verified",
            confidence=round(0.85 + (h % 15) / 100.0, 2),
        )
