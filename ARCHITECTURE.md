# CARAXES Architecture

## Current implementation

The active text chat path is:

```text
Client
  -> POST /api/chat
  -> FastAPI chat route
  -> bounded Nebius tool-calling loop
     -> controlled workspace tools (list, read, search only)
  -> Nebius Token Factory (OpenAI-compatible chat completions)
  -> NVIDIA Nemotron
  -> {"response": "..."}
```

The documented API base URL is `https://api.tokenfactory.nebius.com/v1/`. Authentication uses the `NEBIUS_API_KEY` environment variable. The model identifier is configured with `NEBIUS_MODEL`.

`GET /health` is independent of the LLM provider. The chat API accepts `{ "message": "..." }` and returns `{ "response": "..." }`. The agent can make at most three tool-call rounds. Its only tools list directories, read UTF-8 text files, and search text files under the existing `CARAXES_WORKSPACE` directory (default `backend/CARAXES_WORKSPACE`); paths resolving outside that root are rejected. The agent does not create or modify workspace content.

Separate local voice utilities exist:

```text
Microphone recording (backend/app/voice/audio.py)
  -> faster-whisper transcription (backend/app/voice/speech_to_text.py)
```

The wake-word utility in `backend/app/voice/wake_word.py` currently loads openWakeWord's bundled `hey_jarvis` model. It is not a Caraxes model and is not wired to the chat route or an activation loop. The microphone test script in `backend/app/voice/test_stt.py` still uses the legacy Gemini helper; `/api/chat` uses Nebius and does not fall back to Gemini.

## Planned architecture

The following is a target, not current behavior:

```text
Microphone
  -> wake-word activation
  -> speech-to-text
  -> assistant reasoning (Nebius/Nemotron)
  -> validated tools / approved knowledge sources
  -> permission and confirmation checks
  -> action execution and verification
  -> response / text-to-speech
```

Real-time activation, web research, RAG, memory, a permission system, TTS, and desktop UI are not connected to the current chat endpoint. Phase 5 currently implements only bounded read-only workspace tools; it does not enable file changes, shell execution, web access, or unrestricted computer control.

## Provider decision

Phase 4 uses the official Nebius Token Factory OpenAI-compatible chat API and a Nemotron model listed in Nebius’s public [model catalog](https://tokenfactory.nebius.com/model-catalog.md). See [ADR-001](./docs/decisions/ADR-001-nebius-nemotron.md).
