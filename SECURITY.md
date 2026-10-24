# Security

## Current safeguards

- `LLM_PROVIDER` explicitly selects `nebius` or `gemini`; credentials and model names are read only for the selected provider.
- Nebius uses `NEBIUS_API_KEY` and `NEBIUS_MODEL`; Gemini uses `GEMINI_API_KEY` and `GEMINI_MODEL`. Store credentials in the ignored `backend\.env`.
- `.env` files must never be committed. No API key belongs in source, examples, logs, or API responses.
- The chat route sends the user's message and configured model to Nebius Token Factory for inference.
- Provider errors returned to clients do not include raw SDK exceptions or credentials.
- The bounded chat agent exposes only `list_directory`, `read_file`, and `search_files` within the existing `CARAXES_WORKSPACE` (default `backend/CARAXES_WORKSPACE`). Paths are relative; resolved paths outside the root are rejected.
- Text reads/search are limited to 1 MB per file and search returns at most 100 matches. The agent stops after three tool-call rounds.
- No shell, write, delete, web, or computer-control tools are exposed. Workspace content is treated as untrusted prompt input.

## Future requirements

Any future action tools must follow least privilege, be isolated to an explicitly approved workspace, validate all inputs, and require explicit user confirmation for dangerous operations. Results of important actions must be verified before CARAXES reports success. A broader permission manager and action verification system are planned and do not yet exist.
