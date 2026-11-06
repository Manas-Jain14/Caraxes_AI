# CARAXES Product Requirements

## Product vision

CARAXES is intended to become a local-first, multilingual (English, Hindi, and Hinglish), voice-first personal AI desktop agent for Windows. It should support voice and text, plan and execute bounded multi-step tasks, and interact with local files and applications only through controlled, user-approved capabilities.

The long-term product may use remote LLM inference where appropriate. Users must be told when private document content will be sent to a cloud provider.

## Current product state

### Implemented

- FastAPI `GET /health` and `POST /api/chat`.
- Gemini and Nebius provider adapters selected through `LLM_PROVIDER`, behind a shared provider interface.
- A bounded agent loop with workspace tools for listing, reading, searching, and writing files. Tools are restricted to `CARAXES_WORKSPACE`.
- Local audio recording, faster-whisper transcription, and standalone openWakeWord detection using the pretrained `hey_jarvis` model.
- Tests for the API, agent/provider behavior, and workspace tools.

### Partially implemented

- Workspace path checks reject traversal and resolved paths outside the configured workspace, and text operations enforce size limits. Symlink escapes are checked, but race-condition protection is not guaranteed.
- `write_file` is exposed to the agent and writes directly, including creating parent directories and overwriting a file. There is no centralized permission manager, explicit approval flow, audit log, or action verification framework.
- Recording, transcription, and wake-word detection exist as separate utilities, but do not form an integrated conversation flow.
- Custom wake-word training materials and scripts exist; runtime detection still uses the pretrained `hey_jarvis` model. A production Caraxes model is not implemented.

### Planned

- A Tauri + React + TypeScript Windows desktop interface with a central 3D agent-state visualization using Three.js / React Three Fiber.
- Integrated voice and text interaction, wake-word activation, and text-to-speech.
- Multi-step planning and controlled interaction with local files and applications.
- Browser automation or direct API integrations, using appropriately controlled tools.
- User-approved persistent memory and document understanding/RAG.
- SQLite as the initial persistence layer.

## Product goals

- Provide a testable backend chat interface with configurable Gemini and Nebius providers.
- Develop toward useful English, Hindi, and Hinglish interaction without making unverified language-quality claims.
- Keep execution bounded, visible, and controlled by explicit user permissions rather than model output.
- Prefer local processing for local resources where practical, and disclose cloud processing when user content is sent remotely.

## Functional requirements and status

| Capability | Status | Notes |
| --- | --- | --- |
| Text chat | Implemented | `POST /api/chat` accepts a non-empty message and returns a response. |
| Provider selection | Implemented | `LLM_PROVIDER=nebius` or `LLM_PROVIDER=gemini`; selected provider credentials and model are required. No automatic fallback. |
| Workspace listing, reading, and search | Implemented | Bounded tools operate within `CARAXES_WORKSPACE`. |
| Workspace writing | Implemented, without approval controls | `write_file` can create parent directories and write or overwrite UTF-8 files within the workspace. |
| English, Hindi, and Hinglish | Intended; quality not separately verified | The current API forwards text to the selected model; no language detection or quality guarantee exists. |
| Audio recording and transcription | Partially implemented | Local utilities only; not connected to chat. |
| Wake-word activation | Partially implemented | Standalone detector uses pretrained `hey_jarvis`, not a production Caraxes model; no activation loop is connected. |
| Text-to-speech and full voice conversation | Planned | No TTS implementation or integrated voice-to-agent pipeline exists. |
| Desktop UI and 3D state visualization | Planned | No Tauri or frontend application exists. |
| Browser/application actions, persistent memory, and RAG | Planned | Not implemented. |

## Safety and trust requirements

LLM output must never authorize its own actions. A centralized permission manager must control sensitive operations, and destructive or sensitive actions must require explicit user approval. Tool schemas and arguments must be strictly validated. Filesystem operations must stay within approved workspaces and account for traversal, symlink escapes, and race conditions. Avoid unrestricted shell execution and arbitrary code execution. Apply timeouts and resource limits, record meaningful tool actions in audit logs, support cancellation, and verify important actions before reporting success.

These are requirements for future hardening and expanded capabilities; they are not all implemented today. The current agent can invoke `write_file` without user approval. See [SECURITY.md](./SECURITY.md) for implemented safeguards and gaps.

## Provider and privacy requirements

The selected provider is configured with `LLM_PROVIDER`, `NEBIUS_API_KEY` / `NEBIUS_MODEL`, or `GEMINI_API_KEY` / `GEMINI_MODEL`. Provider pricing and availability depend on current account terms; neither is guaranteed free. Requests, including any workspace content returned to the agent as tool results, are sent to the selected cloud provider. Users must be informed before private documents are processed this way.

## Acceptance direction

Future product increments should ship in dependency-aware stages: establish permission and safety controls before expanding sensitive actions; integrate the standalone voice components before claiming an end-to-end voice assistant; and add desktop, browser, memory, or RAG features only with their security, privacy, and verification behavior defined.
