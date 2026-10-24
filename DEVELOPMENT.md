# CARAXES Development Guide

## Development rules

- Prefer minimum code, maximum clarity.
- Work on one phase at a time; do not implement future phases prematurely.
- Inspect existing code and documentation before editing.
- Reuse current modules and preserve unrelated behavior.
- Test the change before moving to another phase.
- Never hardcode or commit secrets; keep `.env` local and ignored.
- Do not give a model unrestricted shell or computer access.

## Local backend setup

From the repository root in PowerShell:

```powershell
cd .\backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Add a Nebius Token Factory key to `backend\.env`, then run:

```powershell
uvicorn app.main:app --reload
```

## Focused backend tests

```powershell
cd .\backend
python -m unittest discover -s tests
```

The API smoke checks are `GET /health` and `POST /api/chat`; see [API.md](./API.md).

## Git workflow

Use a feature branch, then focused commits, push, and open a pull request for review. Do not push feature work directly to `main` or merge it without approval.
