# Outreach Pipeline

Automated cold outreach pipeline: give one seed company domain, and the system
finds similar companies, discovers decision makers, resolves verified emails,
and sends personalized outreach -- all in a single command.

## Architecture

```
Seed Domain
    |
    v
[Stage 1: Ocean.io]       -> Similar company domains
    |
    v
[Stage 2: Prospeo]        -> Decision makers + LinkedIn URLs
    |
    v
[Stage 3: Eazyreach]      -> Verified work emails
    |
    v
[Safety Checkpoint]        -> Review recipients, confirm y/N
    |
    v
[Stage 4: Brevo]          -> Personalized outreach emails sent
    |
    v
runs/YYYYMMDD-HHMMSS-domain/
    companies.json
    decision_makers.json
    resolved_contacts.json
    email_drafts.json
    send_results.json
    failures.json
    summary.json
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy and configure environment variables (optional for mock mode)
cp .env.example .env

# 3. Default run (Mock mode, stages 1-3, generates drafts, stops before sending)
python -m outreach.cli run stripe.com --mode mock --limit 5

# 4. Mock simulated send (Runs full mock pipeline and simulates sending emails)
python -m outreach.cli run stripe.com --mode mock --limit 5 --send --yes

# 5. Real mode (Always shows safety checkpoint, ignores --yes)
python -m outreach.cli run stripe.com --mode real --limit 5 --send
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `python -m outreach.cli run <domain> [options]` | Run the full pipeline |
| `python -m outreach.cli history` | Show past runs |
| `python -m outreach.cli --version` | Show version |
| `python -m outreach.cli --help` | Show help |

### Run Options

| Option | Default | Description |
|--------|---------|-------------|
| `--mode` | `mock` | Pipeline mode: `mock` or `real` |
| `--limit` | `5` | Max similar companies to discover |
| `--dry-run / --send` | `--dry-run` | Draft only vs. actually send emails |
| `--yes` | `false` | Auto-confirm checkpoint (mock mode only) |

## Environment Variables

| Variable | Service | Auth Header | Required |
|----------|---------|-------------|----------|
| `OCEAN_API_TOKEN` | Ocean.io | `X-Api-Token` | Real mode only |
| `PROSPEO_API_KEY` | Prospeo | `X-KEY` | Real mode only |
| `EAZYREACH_API_KEY` | Eazyreach | TBD (see docs.eazyreach.app) | Real mode only |
| `BREVO_API_KEY` | Brevo | `api-key` | Real mode only |
| `SENDER_EMAIL` | Brevo | -- | Real mode only |
| `SENDER_NAME` | Brevo | -- | Real mode only |

## Mock vs Real Mode

- **Mock mode** (`--mode mock`): Uses generated sample data. No API keys needed.
  Works out of the box for development, testing, and demos.
- **Real mode** (`--mode real`): Calls actual APIs. All 4 API keys must be set
  in `.env`. The CLI validates keys before starting.

## Safety Checkpoint

Before sending any emails (Stage 4), the CLI displays a summary table of all
recipients and asks for explicit `y/N` confirmation.

- `--yes` auto-confirms the checkpoint **in mock mode only**.
- In real mode, the checkpoint is always shown regardless of `--yes`.

## Project Structure

```
outreach-pipeline/
  outreach/
    __init__.py          # Package root
    cli.py               # Typer CLI entry point
    config.py            # Pydantic Settings from .env
    models.py            # Data models (Company, Person, VerifiedContact, ...)
    pipeline.py          # Orchestrator: chains all 4 stages
    storage.py           # Per-run folder + JSON output writers
    logger.py            # Rich-based structured logging
    utils.py             # Shared utilities
    stages/
      ocean.py           # Stage 1: Ocean.io client
      prospeo.py         # Stage 2: Prospeo client
      eazyreach.py       # Stage 3: Eazyreach client
      brevo.py           # Stage 4: Brevo client
    email/
      templates.py       # Outreach email templates
  tests/
    __init__.py
  runs/                  # Pipeline output (per-run folders)
  .env.example           # Environment variable template
  requirements.txt       # Python dependencies
  README.md              # This file
```

## Testing

```bash
pytest tests/ -v
```

## License

Internal assignment project.
