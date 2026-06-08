"""
Vercel serverless entrypoint.

Vercel's Python runtime looks for a handler in api/*.py files.
This module re-exports the FastAPI app from outreach.api so that
Vercel finds exactly one entrypoint — no ambiguity with cli.py or tests.
"""

from outreach.api import app  # noqa: F401
