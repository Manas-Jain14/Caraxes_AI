# CARAXES Architecture

This document separates the implemented Python backend from the intended desktop-agent architecture.

## Current implementation

```text
Client
  -> FastAPI
     -> GET /health
     -> POST /api/chat
        -> bounded agent loop
           -> list_directory / read_file / search_files / write_file
              -> CARAXES_WORKSPACE
        -> configured provider adapter
           -> Nebius Token Factory (OpenAI-compatible API)
           -> Google Gemini
```

`GET /health` does not contact a model. `POST /api/chat` accepts a non-empty `message` and returns a `response`. The provider factory requires `LLM_PROVIDER=nebius` or `LLM_PROVIDER=gemini`; it does not automatically fall back. Nebius requires `NEBIUS_API_KEY` and `NEBIUS_MODEL`, and uses `https://api.tokenfactory.nebius.com/v1/`. Gemini requires `GEMINI_API_KEY` and `GEMINI_MODEL`. Both adapters implement the same provider interface and normalize provider-specific tool-call formats. Credentials and model identifiers are configured outside source code.

The agent makes at most three tool-call rounds and accepts at most three calls per round. Tool schemas reject additional properties; the dispatcher also checks allowed argument keys. The tools list, read, and search within `CARAXES_WORKSPACE`, and can write UTF-8 text files there. Read/search operations have a 1 MB per-file limit and search returns at most 100 matching lines; writes have a 1 MB limit. `write_file` creates parent directories and can overwrite an existing file without a separate approval step. There are no delete, shell, browser, or operating-system control tools.

Workspace paths are relative. Traversal and paths resolving outside the configured workspace are rejected; symlink escapes are checked during path resolution. These checks do not establish protection against filesystem race conditions. There is no centralized permission manager, approval workflow, audit log, or action verification system.

## Separate local voice utilities

```text
Microphone recording (backend/app/voice/audio.py)
  -> faster-whisper transcription (backend/app/voice/speech_to_text.py)

Audio chunk
  -> standalone openWakeWord detector (backend/app/voice/wake_word.py)
     -> pretrained hey_jarvis model
```

These utilities are not connected to `/api/chat`. Wake-word detection is not a continuous activation loop and does not use a production Caraxes-trained model. There is no TTS implementation or integrated voice-to-agent-to-speech pipeline. `backend/app/voice/test_stt.py` includes a separate legacy Gemini helper; it is not the chat route.

## Intended product architecture (planned)

```text
Windows desktop: Tauri + React + TypeScript
  -> voice and text interaction
     -> wake-word / user-controlled activation
     -> faster-whisper STT and future TTS
     -> Python + FastAPI backend
        -> provider abstraction (initially Gemini and Nebius)
        -> bounded planner and validated tool schemas
        -> centralized permission manager and user approval
        -> controlled local file/application and browser/API integrations
        -> SQLite initial storage for user-approved memory
        -> document understanding / RAG over user-approved sources
  -> Three.js / React Three Fiber visualization of agent states
```

This is a target, not a description of current runtime behavior. The frontend, TTS, permission manager, browser/API integrations, SQLite persistence, memory, and RAG are not implemented. Future sensitive actions must be authorized by explicit user-controlled policy; an LLM response must never grant its own permission.

## Provider decision

The current implementation supports configurable Nebius Token Factory and Google Gemini adapters. Provider availability, model access, pricing, and account terms may vary; neither provider is guaranteed to be free. Any private workspace content returned to a tool call is included in the conversation sent to the selected remote provider. See [SECURITY.md](./SECURITY.md) for privacy and safety boundaries.
