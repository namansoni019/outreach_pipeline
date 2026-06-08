"""
Vercel serverless entrypoint.

Vercel's Python runtime looks for a handler in api/*.py files.
This module re-exports the FastAPI app from outreach.api so that
Vercel finds exactly one entrypoint — no ambiguity with cli.py or tests.
"""

import sys
from pathlib import Path

# Vercel might execute this from the api/ directory without mounting the project root properly
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from outreach.api import app  # noqa: F401
