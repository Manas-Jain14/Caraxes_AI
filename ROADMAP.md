# CARAXES Roadmap

Status reflects code and tests in this repository. Phase 6 provider switching is implemented on its feature branch; authenticated live inference has not been verified.

## Completed

- Phase 1 — Basic FastAPI health/chat API and initial Gemini integration. Gemini is retained only by the legacy microphone test helper; it is not the active chat provider.
- Phase 3A — openWakeWord utility using the bundled `hey_jarvis` model.

## Current

- Phase 3B — Production Caraxes model data/features exist, but production training, export, and validation are incomplete.
- Phase 4 — Nebius + Nemotron provider and focused tests are implemented on `phase-4-nebius-nemotron`. Authenticated live inference and review/merge are pending.
- Phase 5 — bounded Nebius tool calling with three read-only controlled-workspace tools and tests is implemented on `phase-5-agent-tools`; authenticated live inference and review/merge are pending.
- Phase 6 — environment-selected Nebius/Gemini adapters share the existing agent and tools; mocked tests pass, live inference and review/merge are pending.
- Phase 2 voice utilities exist, but do not form an end-to-end voice conversation flow.

## Next

- Configure a Nebius API key locally and verify one authenticated `/api/chat` request, then review and merge Phase 4.
- Complete and validate the Phase 3B production Caraxes model before claiming that phase complete.

## Planned

- Web research, RAG, memory, permissions/action verification, desktop UI, evaluation, and demo polish.

| Phase | Scope | Status |
| --- | --- | --- |
| 1 | Basic FastAPI chat backend | Completed; Gemini remains in legacy microphone test code |
| 2 | Voice utilities | Partial; recording/transcription exist, no end-to-end voice path |
| 3A | openWakeWord utility | Completed with bundled `hey_jarvis` model |
| 3B | Custom Caraxes model | In progress; training/export/validation incomplete |
| 4 | Nebius Token Factory + NVIDIA Nemotron | Provider/tests implemented on feature branch; authenticated live call and review pending |
| 5 | Agent tools | Implemented on `phase-5-agent-tools`: bounded read-only workspace listing, reading, and search |
| 6 | LLM provider abstraction and switching | Implemented on `phase-6-llm-provider-abstraction`; live provider calls pending |
| 7 | Web research | Planned |
| 8 | RAG over user-approved content | Planned |
| 9 | Memory | Planned |
| 10 | Permissions and action verification | Planned |
| 11 | Desktop UI | Planned |
| 12 | Evaluation | Planned |
| 13 | Hackathon/demo polish | Planned |

## Phase 4 boundary

Phase 4 changes only the provider used by `POST /api/chat`, adds required Nebius configuration, and documents/test the integration. It does not add tool calling, web research, RAG, memory, permissions, wake-word runtime integration, or desktop UI.

## Phase 5 boundary

Phase 5 adds a bounded OpenAI-compatible tool-calling loop to `POST /api/chat` with only `list_directory`, `read_file`, and `search_files`, restricted to `CARAXES_WORKSPACE`. It does not add file writes/deletes, shell or OS control, web access, RAG, memory, permissions, wake-word runtime integration, or desktop UI.
