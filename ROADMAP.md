# CARAXES Roadmap

This roadmap separates the implemented repository baseline from the product direction. Status is based on the source and tests in this checkout, not on branch names or unverified live provider calls.

## Status

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Product foundation and documentation alignment | Completed by this documentation milestone |
| 1 | FastAPI chat, Gemini/Nebius provider abstraction, bounded agent loop, and workspace tools | Implemented; live inference requires configured credentials and has not been verified by the unit tests |
| 2 | Local voice utilities | Partial; recording, faster-whisper transcription, and standalone pretrained `hey_jarvis` detection exist; no integrated voice loop or TTS |
| 3 | Permission and safety foundation | Planned; centralized permission manager, explicit approvals, audit logging, cancellation, action verification, and race-condition protections are not implemented |
| 4 | Integrated voice experience | Planned; connect recording/STT, an appropriately validated wake-word flow, agent, and TTS after defining permissions and privacy behavior |
| 5 | Windows desktop interface | Planned; Tauri + React + TypeScript with Three.js / React Three Fiber visualization |
| 6 | Controlled browser and application integrations | Planned; scope, approvals, input validation, timeouts, resource limits, cancellation, and verification required before enabling actions |
| 7 | User-approved memory and document understanding/RAG | Planned; define consent, retention, deletion, and cloud-disclosure behavior first; SQLite is the initial storage intention |
| 8 | Evaluation and release readiness | Planned; test language behavior, safety boundaries, error handling, and supported Windows workflows before product claims |

## Immediate priorities

1. Address the current `write_file` gap with an explicit authorization and confirmation design before expanding sensitive tool capabilities.
2. Define action audit, cancellation, verification, resource/time limits, and defenses for filesystem race conditions.
3. Join the existing local voice utilities into a user-controlled flow; decide on TTS and wake-word behavior without treating custom training as complete.
4. Build the Windows desktop shell and visualization once backend interaction and permission boundaries are stable.
5. Add browser/application actions, then memory and document retrieval, only with their privacy, permission, and verification requirements in place.

## Current implementation boundary

`POST /api/chat` selects Gemini or Nebius with `LLM_PROVIDER` and runs the same bounded agent loop. The agent can make at most three tool-call rounds and at most three tool calls in a round. Available tools are `list_directory`, `read_file`, `search_files`, and `write_file`, all constrained to `CARAXES_WORKSPACE`. Reads/searches are limited to 1 MB per file and searches return at most 100 matching lines; writes are limited to 1 MB and can create directories or overwrite files without an approval flow.

There are no delete, shell, browser, memory, RAG, TTS, or desktop frontend implementations. The voice utilities are standalone. The wake-word detector loads openWakeWord's pretrained `hey_jarvis` model; custom Caraxes training is not a production model.

## Dependency notes

- Permission and safety controls should precede any expansion to destructive, external, browser, or application actions. The existing direct `write_file` behavior should be addressed as part of this work.
- Full voice interaction depends on a clear activation/consent model and connecting the recording, transcription, agent, and speech-output components.
- Desktop work depends on a stable interaction contract and should expose action state and approvals rather than imply unimplemented protections.
- Browser automation and API integrations require strict capability boundaries, timeouts, resource limits, cancellation, and verification.
- Memory and RAG require storage lifecycle, user approval, deletion, and disclosure rules, especially when retrieved private content is sent to a cloud model.
