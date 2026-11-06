# CARAXES Development Guide

## Development rules

- Inspect existing code and documentation before editing.
- Work on one milestone at a time; do not describe planned features as implemented.
- Reuse current modules and preserve unrelated changes.
- Run the focused repository tests for backend changes.
- Never hardcode, expose, or commit credentials. Keep `.env` local and ignored.
- Do not give a model unrestricted shell access or let model output authorize its own actions.

## Windows backend setup (PowerShell)

Use Python 3.10 or newer. From the repository root:

```powershell
Set-Location .\backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

If PowerShell blocks virtual-environment activation, permit it for the current process only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Configure `.env` with:

- `LLM_PROVIDER=nebius` and `NEBIUS_API_KEY` / `NEBIUS_MODEL`, or
- `LLM_PROVIDER=gemini` and `GEMINI_API_KEY` / `GEMINI_MODEL`.

The checked-in example selects Nebius and includes a model identifier, but no credentials. The selected provider must have both its key and model configured. Neither provider is guaranteed free; confirm current pricing and account terms. `CARAXES_WORKSPACE` optionally sets the workspace. Relative values resolve from `backend\`; the example uses `.\CARAXES_WORKSPACE`.

## Run the backend

From `backend\` with the virtual environment active:

```powershell
uvicorn app.main:app --reload
```

The implemented endpoints are `GET /health` and `POST /api/chat`; see [API.md](./API.md). A live chat request requires valid credentials and a model for the selected provider.

## Run backend tests

From `backend\` with the virtual environment active:

```powershell
python -m unittest discover -s tests -v
```

The suite uses `unittest`; provider behavior is tested with mocked clients, so passing unit tests do not establish live provider availability.

## Security boundary

The bounded workspace agent includes `write_file`, which can create or overwrite a file without user approval. Until a permission manager and confirmation flow are implemented, use only a workspace whose contents and writes you are willing to expose to the configured model and modify directly. Review [SECURITY.md](./SECURITY.md) before adding or using tools that access sensitive resources.

## Git workflow

Use a feature branch for focused work. Do not push directly to `main`. Commit, push, and open a pull request only when requested and after the relevant review.
