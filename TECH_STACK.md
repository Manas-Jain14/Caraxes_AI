# CARAXES Technology Stack

Status distinguishes what is present in this repository from the intended product architecture.

## Implemented

| Technology | Purpose | Status / boundary |
| --- | --- | --- |
| Python | Backend and local voice utilities | Implemented |
| FastAPI, Uvicorn | HTTP API and ASGI server | Implemented; `/health` and `/api/chat` |
| Shared provider interface | Normalize model requests and tool calls | Implemented |
| Nebius Token Factory, OpenAI Python client | Hosted inference adapter | Implemented; requires `NEBIUS_API_KEY` and `NEBIUS_MODEL` |
| Google Gemini, `google-genai` | Hosted inference adapter | Implemented; requires `GEMINI_API_KEY` and `GEMINI_MODEL` |
| Configured LLM selection | Select `nebius` or `gemini` using `LLM_PROVIDER` | Implemented; no automatic fallback |
| Python filesystem APIs | Workspace list/read/search/write tools | Implemented; constrained to `CARAXES_WORKSPACE`; write is not approval-gated |
| python-dotenv | Load local `.env` configuration | Implemented |
| faster-whisper | Local speech-to-text utility | Implemented as a standalone utility |
| sounddevice, soundfile | Microphone recording and WAV handling | Implemented as standalone utilities |
| openWakeWord | Wake-word utility | Implemented with pretrained `hey_jarvis`; custom Caraxes production model is not implemented |
| `unittest` | Backend test suite | Implemented; tests cover API, agent/provider behavior, and workspace tools |

Neither remote provider is guaranteed to be free. Availability and pricing depend on provider account terms and current service configuration.

## Intended stack (planned)

| Technology | Intended purpose | Status |
| --- | --- | --- |
| Tauri | Windows desktop application shell | Planned |
| React, TypeScript | Desktop interface and interaction surfaces | Planned |
| Three.js / React Three Fiber | Central 3D visualization reflecting agent states | Planned |
| Python, FastAPI | Desktop-to-agent backend contract | Backend exists; desktop integration is planned |
| Gemini and Nebius adapters | Initial remote LLM providers behind an abstraction | Both adapters exist; provider operation is subject to account access |
| faster-whisper | Local speech recognition in an integrated voice flow | Standalone utility exists; integration is planned |
| Wake-word activation and TTS | Hands-free activation and spoken responses | Planned; no integrated wake-word loop or TTS implementation |
| Playwright or controlled equivalent | Permission-bounded browser automation | Planned; not present in the current request path |
| SQLite | Initial local persistence for user-approved memory | Planned; no database or persistent memory is implemented |
| Document processing / RAG | Retrieve from user-approved documents | Planned; no RAG implementation exists |

The planned technologies are intentions, not current runtime dependencies. No orchestration framework or vector database is selected in this stack.
