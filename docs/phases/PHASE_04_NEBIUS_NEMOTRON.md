# Phase 4 — Nebius Token Factory + NVIDIA Nemotron

## Objective

Route the existing FastAPI chat endpoint through Nebius Token Factory to a currently catalogued NVIDIA Nemotron model for the Nebius x NVIDIA Global AI Hackathon. Do not claim hackathon compliance until an authenticated runtime request succeeds and the event rules are checked.

## Starting architecture

`POST /api/chat` called the existing Gemini helper and returned `{"response": ...}`. The microphone test also calls that helper independently. `GET /health` does not use an LLM.

## Changes

- Replaced the provider used by `/api/chat` with the Nebius provider.
- Kept the request body and successful response body unchanged.
- Added configuration and basic upstream/configuration error handling.
- Retained the Gemini helper for the existing voice test; it is not a chat fallback.
- Added focused API tests and project documentation.

## Configuration

- `NEBIUS_API_KEY`: Nebius Token Factory API key, stored outside source control.
- `NEBIUS_MODEL`: defaults in `.env.example` to `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`.
- Base URL: `https://api.tokenfactory.nebius.com/v1/`.
- Requests use OpenAI-compatible chat completions through the OpenAI Python client.

The selected model appears in Nebius's [public model catalog](https://tokenfactory.nebius.com/model-catalog.md). Model availability, account access, and hackathon eligibility should be checked against the live service and official event rules.

## API behavior

- `GET /health` remains `{"status":"ok"}`.
- `POST /api/chat` still accepts `{"message":"..."}` and returns `{"response":"..."}`.
- Missing Nebius configuration returns `503`; upstream errors and empty responses return `502`.
- Invalid request input is rejected by FastAPI/Pydantic validation.

## Testing

- `python -m unittest discover -s tests -v`: 9 tests passed, covering health, chat response shape, validation, provider configuration, empty responses, and upstream errors.
- Python compilation passed.
- Live `GET /health` returned `{"status":"ok"}`.
- `POST /api/chat` without a configured Nebius API key returned the expected `503`.
- A live `POST /api/chat` attempt returned `503` because Nebius credentials are not configured; no authenticated provider request was made.

## Known limitations

- Agent/tool calling is **not implemented** in this phase.
- Voice capture, STT, TTS, wake-word runtime integration, and the Gemini-based microphone test are unchanged.
- No fallback provider, retry framework, performance comparison, or model evaluation was added.
- Event eligibility depends on hackathon rules and is not inferred from model availability alone.

## Files changed

Implementation files: `backend/app/api/chat.py`, `backend/app/ai/nebius.py`, `backend/requirements.txt`, `backend/.env.example`, and `backend/tests/test_chat.py`. Documentation files: `AGENTS.md`, `README.md`, `PRD.md`, `ARCHITECTURE.md`, `DEVELOPMENT.md`, `ROADMAP.md`, `SECURITY.md`, `API.md`, `TECH_STACK.md`, `docs/phases/PHASE_04_NEBIUS_NEMOTRON.md`, and `docs/decisions/ADR-001-nebius-nemotron.md`. The Gemini helper and voice code remain unchanged.

## Next phase

First verify one authenticated Nebius request locally, then complete review/merge. After that, proceed only according to the roadmap. Agent tools are a future phase and are not part of this integration.
