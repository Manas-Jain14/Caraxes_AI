# Phase 5 — Bounded Agent Tools

## Status

Implemented on `phase-5-agent-tools`. Authenticated live Nebius inference has not been verified.

## Implemented scope

`POST /api/chat` uses a bounded OpenAI-compatible tool-calling loop with exactly three registered read-only tools:

- `list_directory` lists entries under the controlled workspace.
- `read_file` reads UTF-8 text files up to 1 MB.
- `search_files` searches UTF-8 text files up to 1 MB, returning at most 100 matching lines and skipping non-text or oversized files.

The existing workspace is configured with `CARAXES_WORKSPACE` or defaults to `backend/CARAXES_WORKSPACE`. Relative paths are resolved and checked against the workspace root, including symlink resolution. The agent allows no more than three tool-call rounds and does not create or modify workspace content.

## Explicitly out of scope

This phase adds no file creation, modification, or deletion; command execution; web access; RAG; memory; permissions/confirmation system; wake-word runtime integration; or desktop UI.

## Validation

Focused unit tests mock Nebius responses and cover the bounded loop and workspace path restrictions. No credentials are required for those tests. A live authenticated inference check remains pending.
