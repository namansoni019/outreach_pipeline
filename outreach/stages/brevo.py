"""
Brevo API client -- Stage 4: send personalized outreach emails.

Auth:
    Header: api-key
    Env var: BREVO_API_KEY
    Endpoint: POST https://api.brevo.com/v3/smtp/email (confirmed)

Uses direct httpx calls (no SDK dependency) for transparency and control.
Includes a 1-second delay between sends to respect rate limits.
"""

from __future__ import annotations

import time

import httpx

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

from outreach.models import EmailDraft, EmailSendResult

# --------------------------------------------------------------------- #
# API Constants (confirmed from Brevo docs)
# --------------------------------------------------------------------- #
BASE_URL = "https://api.brevo.com"
SEND_EMAIL_ENDPOINT = "/v3/smtp/email"


def is_retryable(exception: BaseException) -> bool:
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code == 429 or exception.response.status_code >= 500
    return isinstance(exception, httpx.RequestError)


class BrevoClient:
    """Client for the Brevo transactional email API."""

    def __init__(
        self,
        api_key: str,
        sender_email: str,
        sender_name: str,
    ) -> None:
        self.api_key = api_key
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(is_retryable),
    )
    def send_email(self, draft: EmailDraft) -> EmailSendResult:
        """Send a single email via Brevo's transactional API."""
        payload = {
            "sender": {
                "email": self.sender_email,
                "name": self.sender_name,
            },
            "to": [
                {
                    "email": draft.to_email,
                    "name": draft.contact_name,
                }
            ],
            "subject": draft.subject,
            "textContent": draft.body,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{BASE_URL}{SEND_EMAIL_ENDPOINT}",
                    headers=self.headers,
                    json=payload,
                )
                if response.status_code == 429 or response.status_code >= 500:
                    response.raise_for_status()
                    
                response.raise_for_status()

            data = response.json()
            return EmailSendResult(
                to_email=draft.to_email,
                status="sent",
                provider_message_id=data.get("messageId"),
            )
        except httpx.HTTPError as exc:
            return EmailSendResult(
                to_email=draft.to_email,
                status="failed",
                error=str(exc),
            )


# --------------------------------------------------------------------- #
# Mock Client
# --------------------------------------------------------------------- #

class MockBrevoClient:
    """Mock Brevo client that simulates sending without real API calls."""

    def send_email(self, draft: EmailDraft) -> EmailSendResult:
        """Return simulated send result. No real emails are sent."""
        import time
        import uuid

        time.sleep(0.1)
        
        return EmailSendResult(
            to_email=draft.to_email,
            status="sent",
            provider_message_id=f"mock-{uuid.uuid4().hex[:12]}",
        )

