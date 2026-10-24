# CARAXES

CARAXES is a voice-first AI assistant prototype, developed incrementally for English, Hindi, and Hinglish interaction. The current backend exposes a text chat API with a bounded, read-only workspace agent and local voice utilities; memory and desktop integration are not implemented.

## Current status

### Implemented

- FastAPI `GET /health` and `POST /api/chat`.
- `POST /api/chat` uses the provider selected by `LLM_PROVIDER` (Nebius/Nemotron or Gemini) and can use three read-only workspace tools: `list_directory`, `read_file`, and `search_files`.
- Workspace tools are restricted to `CARAXES_WORKSPACE` (default `backend\CARAXES_WORKSPACE`) and the agent is limited to three tool-call rounds. No write, delete, shell, or web tools are available.
- Local microphone recording, faster-whisper transcription, and a separate openWakeWord utility exist. The wake-word utility currently loads the bundled `hey_jarvis` model, not a Caraxes model.

### In progress

- Phase 3B production Caraxes wake-word model training and validation.
- Phase 4 Nebius + Nemotron integration is implemented on `phase-4-nebius-nemotron`; authenticated live inference and review/merge remain pending.

### Planned

- Real-time wake-word activation, web research, RAG, memory, permissions, action verification, and a desktop UI.

## Current architecture

```text
Chat client
  -> POST /api/chat (FastAPI)
  -> bounded agent loop (read-only workspace tools)
  -> provider interface
     -> Nebius Token Factory / NVIDIA Nemotron, or
     -> Google Gemini
  -> {"response": "..."}
```

Workspace tools can list directories, read UTF-8 text files up to 1 MB, and search UTF-8 text files up to 1 MB within the configured workspace. Paths are relative; traversal and paths resolving outside the workspace are rejected. Search returns at most 100 matches and skips non-text or oversized files.

Provider selection changes only the LLM adapter; agent and tool logic remain shared. The voice utilities are not connected to this chat route. The existing microphone test script retains its separate Gemini helper.

## Tech stack

| Technology | Purpose | Status |
| --- | --- | --- |
| Python, FastAPI | Backend and HTTP API | Implemented |
| Nebius Token Factory, OpenAI Python client | Optional main-chat provider | Implemented |
| NVIDIA Nemotron 3 Nano 30B A3B | Nebius chat model | Configured |
| Google GenAI SDK | Optional Gemini chat provider | Implemented |
| faster-whisper, sounddevice, soundfile | Local speech transcription and audio utilities | Implemented utilities |
| openWakeWord | Wake-word detection utility and training workflow | Implemented utility; custom model in progress |
| Gemini (`google-genai`) | Legacy microphone test helper only | Retained; not used by `/api/chat` |
| LangGraph, Qdrant, Tauri, React, TypeScript, Piper TTS | Future orchestration, retrieval, desktop UI, and speech output | Planned |

## Setup

Use Python 3.10 or newer. From the repository root:

```powershell
cd .\backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Set `LLM_PROVIDER` and the matching provider credentials/model in `backend\.env`; never commit `.env`. The checked-in configuration selects Nebius by default.
`CARAXES_WORKSPACE` optionally selects the controlled workspace; relative values resolve from `backend\`. The default workspace directory is included in the repository, and its contents are ignored by Git. Add files or folders to it yourself; the agent tools do not create or modify workspace content.

## Run the backend

From `backend\` with the environment active:

```powershell
uvicorn app.main:app --reload
```

## API smoke tests

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Chat request:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat `
  -ContentType "application/json" -Body '{"message":"Reply with a short greeting."}'
```

Response shape:

```json
{"response":"<model-generated text>"}
```

## LLM provider configuration

During the Nebius x NVIDIA hackathon, set `LLM_PROVIDER=nebius`; the backend uses `NEBIUS_API_KEY` and `NEBIUS_MODEL` (default `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`) with Nebius Token Factory.

After the hackathon, switch to Gemini by setting `LLM_PROVIDER=gemini`, `GEMINI_API_KEY`, and `GEMINI_MODEL`. No agent, tool, voice, RAG, memory, or API route code changes are needed. The selected provider must be configured explicitly; invalid provider names and missing credentials fail clearly without fallback.

Set `GEMINI_MODEL` to the Gemini model enabled for your API key; this project has no prior Gemini model default. Both modes share the same bounded agent and tool-calling logic. Live inference requires credentials for the selected provider.

## Roadmap

See [ROADMAP.md](./ROADMAP.md) for implementation status and planned phases.

## Security

Keep API credentials in environment variables or ignored `.env` files. Do not place secrets in source code or return them from API errors. The agent exposes only read/list/search tools within its configured workspace; it has no shell, write, delete, or web access. These read-only tools do not provide a broader permission manager or confirmation system.

No repository-level open-source license is currently present. Third-party components retain their own licenses.

## Hackathon context

The Phase 4 integration targets the Nebius x NVIDIA Global AI Hackathon by using Nebius Token Factory to serve NVIDIA Nemotron for the main chat path. The current implementation is a backend inference integration only; it does not add agentic task execution or claim unverified model performance or event eligibility.
