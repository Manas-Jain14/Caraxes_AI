# CARAXES Technology Stack

## Current / implemented

| Technology | Purpose | Status |
| --- | --- | --- |
| Python | Backend and voice utilities | Implemented |
| FastAPI, Uvicorn | HTTP API and ASGI server | Implemented |
| Nebius Token Factory | Hosted inference for the main `/api/chat` route | Implemented on Phase 4 branch; authenticated live request pending |
| OpenAI Python client | OpenAI-compatible Nebius chat request | Implemented on Phase 4 branch |
| NVIDIA Nemotron 3 Nano 30B A3B | Configured language model | Implemented on Phase 4 branch; availability is account/region dependent |
| OpenAI-compatible tool calling | Bounded agent loop for `/api/chat` | Implemented on Phase 5 branch; three read-only workspace tools only |
| Python filesystem APIs | Controlled workspace listing, UTF-8 text reading, and search | Implemented on Phase 5 branch; constrained to `CARAXES_WORKSPACE` |
| python-dotenv | Local environment configuration | Implemented |
| faster-whisper | Local speech-to-text utility | Implemented |
| sounddevice, soundfile | Local audio recording and WAV handling | Implemented |
| openWakeWord | Wake-word utility and custom training workflow | Utility exists; production custom model is in progress |
| Google Gemini / `google-genai` | Legacy microphone test helper only | Retained; not the active `/api/chat` provider |

## Planned

| Technology | Intended purpose | Status |
| --- | --- | --- |
| LangGraph | Agent orchestration | Planned |
| Qdrant | Vector retrieval for RAG | Planned |
| Tauri, React, TypeScript | Desktop UI | Planned |
| Piper TTS | Speech synthesis | Planned; not selected for production |
| Database and persistent memory | Long-term assistant state | Planned |

No planned technology above is active in the current chat request path.
