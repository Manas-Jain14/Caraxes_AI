# CARAXES

CARAXES is intended to become a local-first, multilingual (English, Hindi, and Hinglish), voice-first personal AI desktop agent. The current repository is an early backend prototype: it provides a text chat API, bounded workspace tools, and separate local voice utilities. The intended desktop application and integrated voice experience are not implemented yet.

## Status at a glance

### Implemented

- FastAPI `GET /health` and `POST /api/chat`.
- A shared provider interface with configuration-selected Gemini and Nebius adapters.
- A bounded agent loop with `list_directory`, `read_file`, `search_files`, and `write_file` tools, restricted to `CARAXES_WORKSPACE`.
- Local microphone recording, faster-whisper transcription, and standalone openWakeWord detection using the pretrained `hey_jarvis` model.
- Unit tests covering API, agent/provider behavior, and workspace tools.

### Limitations and partial work

- `write_file` can create parent directories and write or overwrite UTF-8 files directly; no centralized permission manager, approval workflow, or action audit log exists.
- Workspace tools reject traversal and resolved paths outside the workspace, including symlink escapes detected during validation. Race-condition resistance is not guaranteed.
- Voice recording, transcription, and wake-word detection are separate utilities. There is no integrated voice-to-agent-to-TTS flow, and no TTS implementation.
- Custom wake-word training materials and scripts exist, but there is no production Caraxes wake-word model. Runtime detection uses the pretrained `hey_jarvis` model.

### Planned

- A Windows desktop application built with Tauri, React, and TypeScript, with a central 3D visualization using Three.js / React Three Fiber.
- Integrated voice and text interaction, wake-word activation, and text-to-speech.
- User-approved permissions for sensitive actions, robust action verification, and cancellation.
- Controlled browser automation or direct API integrations, user-approved persistent memory, and document understanding/RAG.
- SQLite as the initial persistence layer. These components are architectural intentions, not dependencies or implemented features in the current request path.

See [PRD.md](./PRD.md), [ARCHITECTURE.md](./ARCHITECTURE.md), and [ROADMAP.md](./ROADMAP.md) for requirements, boundaries, and sequence.

## Current chat behavior

The backend exposes:

- `GET /health` — returns `{"status":"ok"}` without contacting a model.
- `POST /api/chat` — accepts `{"message":"..."}` and returns `{"response":"..."}`.

The agent makes at most three tool-call rounds and accepts at most three tool calls in a round. Its tools list directories, read UTF-8 text files, search text files, and write UTF-8 text files inside the configured workspace. Read and search operations limit each file to 1 MB; search returns at most 100 matching lines. Writes are limited to 1 MB. There are no delete, shell, or browser tools.

Workspace tool paths must be relative. Traversal and paths that resolve outside the workspace are rejected; symlink escapes are checked. The implementation does not provide centralized authorization, approval, or race-condition guarantees. In particular, a model-generated tool call can invoke `write_file` without user confirmation.

## Windows setup (PowerShell)

Use Python 3.10 or newer. From the repository root:

```powershell
Set-Location .\backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

If PowerShell blocks activation, allow it for this terminal only, then activate:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Set `LLM_PROVIDER` to `nebius` or `gemini` in `backend\.env`, and provide the matching API key and model. The checked-in `.env.example` selects Nebius and supplies a Nebius model identifier; it does not contain credentials. The application requires an explicit provider selection and does not fall back between providers. Gemini requires both `GEMINI_API_KEY` and `GEMINI_MODEL`; Nebius requires both `NEBIUS_API_KEY` and `NEBIUS_MODEL`. Neither provider is guaranteed to be free; check the provider's current pricing and account terms.

`CARAXES_WORKSPACE` selects the workspace. A relative value resolves from `backend\`; the example uses `.\CARAXES_WORKSPACE`. Never put credentials in the workspace or commit `.env`. See [SECURITY.md](./SECURITY.md) before using private documents with a cloud provider.

## Run and test

With the virtual environment active and the working directory at `backend\`:

```powershell
uvicorn app.main:app --reload
```

Run the repository's unit tests from `backend\`:

```powershell
python -m unittest discover -s tests -v
```

The provider tests mock network clients. A real `/api/chat` request requires valid credentials and a configured model for the selected provider.

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Chat request:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat `
  -ContentType "application/json" -Body '{"message":"Reply with a short greeting."}'
```

## Product direction

The long-term target is local execution on Windows with remote LLM inference where appropriate. The intended backend is Python and FastAPI, with provider adapters initially for Gemini and Nebius. The planned desktop is Tauri + React + TypeScript. Planned voice work builds on faster-whisper; wake-word integration and TTS remain future work. Browser automation, if added, will use Playwright or another appropriately controlled integration. SQLite is the initial storage intention, and Three.js / React Three Fiber are intended for the agent-state visualization.

These are plans, not claims that a desktop frontend, browser integration, memory, RAG, TTS, SQLite store, or 3D visualization already exists.
