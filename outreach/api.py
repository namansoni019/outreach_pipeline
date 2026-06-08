import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any

from outreach.pipeline import run_pipeline
from outreach.config import load_settings
from outreach.storage import (
    RUNS_DIR,
    load_json,
    COMPANIES_FILE,
    DECISION_MAKERS_FILE,
    RESOLVED_CONTACTS_FILE,
    EMAIL_DRAFTS_FILE,
    SEND_RESULTS_FILE,
    FAILURES_FILE,
    SUMMARY_FILE,
)

app = FastAPI(title="Outreach Pipeline API")

# Allow CORS for Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunRequest(BaseModel):
    domain: str
    mode: str = "mock"
    limit: int = 5
    dry_run: bool = True
    auto_confirm: bool = False

@app.post("/api/runs")
def create_run(req: RunRequest):
    if not req.domain:
        raise HTTPException(status_code=400, detail="Domain is required")
        
    settings = load_settings()
    summary = run_pipeline(
        seed_domain=req.domain,
        settings=settings,
        mode=req.mode,
        limit=req.limit,
        dry_run=req.dry_run,
        auto_confirm=req.auto_confirm
    )
    
    # Extract the run_id from summary.run_dir (it stores the run_id)
    run_id = Path(summary.run_dir).name if summary.run_dir else None
    
    return {
        "run_id": run_id,
        "summary": summary.model_dump(),
        "run_dir": summary.run_dir
    }

@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    run_dir = RUNS_DIR / run_id
    if not run_dir.exists() or not run_dir.is_dir():
        raise HTTPException(status_code=404, detail="Run not found")
        
    summary = load_json(run_dir, SUMMARY_FILE)
    companies = load_json(run_dir, COMPANIES_FILE) or []
    makers = load_json(run_dir, DECISION_MAKERS_FILE) or []
    contacts = load_json(run_dir, RESOLVED_CONTACTS_FILE) or []
    drafts = load_json(run_dir, EMAIL_DRAFTS_FILE) or []
    results = load_json(run_dir, SEND_RESULTS_FILE) or []
    failures = load_json(run_dir, FAILURES_FILE) or []
    
    return {
        "summary": summary,
        "companies": companies,
        "decisionMakers": makers,
        "resolvedContacts": contacts,
        "emailDrafts": drafts,
        "sendResults": results,
        "failures": failures
    }
