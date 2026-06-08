"""
Configuration management via Pydantic Settings + python-dotenv.

Reads from .env file at project root. In mock mode, API keys are not required.
"""

from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# Project root: two levels up from this file (outreach-pipeline/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Default .env path
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """All configuration for the outreach pipeline."""

    # ------------------------------------------------------------------ #
    # Ocean.io -- Stage 1: seed domain -> similar companies
    # Auth header: X-Api-Token
    # ------------------------------------------------------------------ #
    OCEAN_API_TOKEN: str = Field(default="", description="Ocean.io API token")

    # ------------------------------------------------------------------ #
    # Prospeo -- Stage 2: company domains -> decision makers
    # Auth header: X-KEY
    # Base URL: https://api.prospeo.io
    # ------------------------------------------------------------------ #
    PROSPEO_API_KEY: str = Field(default="", description="Prospeo API key")

    # ------------------------------------------------------------------ #
    # Eazyreach -- Stage 3: LinkedIn URLs -> verified emails
    # Auth header: TBD (see docs.eazyreach.app)
    # ------------------------------------------------------------------ #
    EAZYREACH_API_KEY: str = Field(default="", description="Eazyreach API key")

    # ------------------------------------------------------------------ #
    # Brevo -- Stage 4: send personalized outreach emails
    # Auth header: api-key
    # Endpoint: POST https://api.brevo.com/v3/smtp/email
    # ------------------------------------------------------------------ #
    BREVO_API_KEY: str = Field(default="", description="Brevo API key")

    # ------------------------------------------------------------------ #
    # Sender identity
    # ------------------------------------------------------------------ #
    SENDER_EMAIL: str = Field(
        default="outreach@example.com",
        description="From address used in email body signatures",
    )
    SENDER_COMPANY: str = Field(
        default="Acme Inc",
        description="Company name of the sender used in signatures",
    )
    SENDER_NAME: str = Field(
        default="Outreach Pipeline",
        description="From name used in email body signatures",
    )
    
    BREVO_SENDER_EMAIL: str = Field(
        default="",
        description="From address specifically for Brevo sender configuration",
    )
    BREVO_SENDER_NAME: str = Field(
        default="",
        description="From name specifically for Brevo sender configuration. Defaults to SENDER_NAME if empty.",
    )

    model_config = {
        "env_file": str(ENV_FILE) if ENV_FILE.exists() else "",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def has_key(self, stage: str) -> bool:
        """Check whether an API key is configured for the given stage."""
        mapping = {
            "ocean": self.OCEAN_API_TOKEN,
            "prospeo": self.PROSPEO_API_KEY,
            "eazyreach": self.EAZYREACH_API_KEY,
            "brevo": self.BREVO_API_KEY,
            "brevo_sender_email": self.BREVO_SENDER_EMAIL,
        }
        return bool(mapping.get(stage, "").strip())

    def validate_for_real_mode(self) -> list[str]:
        """Return a list of stages missing API keys (empty list = all good)."""
        missing: list[str] = []
        for stage in ("ocean", "prospeo", "eazyreach", "brevo", "brevo_sender_email"):
            if not self.has_key(stage):
                missing.append(stage)
        return missing


def load_settings() -> Settings:
    """Load settings from .env file at project root."""
    return Settings()
