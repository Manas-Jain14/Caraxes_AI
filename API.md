# HTTP API

The API is served by FastAPI (`backend/app/main.py`). Only currently implemented endpoints are listed here.

## `GET /health`

Returns the service health marker without contacting the model provider.

**Request body:** none.

**Response (`200`):**

```json
{"status":"ok"}
```

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## `POST /api/chat`

Sends one text message to the explicitly selected provider (`LLM_PROVIDER=nebius` or `LLM_PROVIDER=gemini`). The bounded agent may call `list_directory`, `read_file`, `search_files`, and `write_file` within the configured workspace. It allows at most three tool-call rounds and three tool calls in a round.

**Request body:**

```json
{"message":"Hello"}
```

`message` must be a non-empty string and is trimmed. A missing, empty, or whitespace-only message is rejected by request validation (`422`).

**Response (`200`):**

```json
{"response":"<model-generated text>"}
```

Missing or unsupported provider configuration, or missing selected-provider credentials/model, returns `503`. A failed upstream request or empty model response returns `502`; secret values and raw provider errors are not returned. Invalid request bodies, including missing, empty, or whitespace-only messages, are rejected with `422`.

### Workspace tools

`CARAXES_WORKSPACE` selects the workspace. Relative values resolve from `backend\`; if unset, the default is `backend\CARAXES_WORKSPACE`. Tool paths are relative to that workspace. Absolute paths, traversal, and paths resolving outside the workspace are rejected. Symlink escapes are checked; filesystem race-condition protection is not guaranteed.

| Tool | Arguments | Behavior and constraints |
| --- | --- | --- |
| `list_directory` | Optional `path` (string; defaults to `.`) | Lists directory entries as names and types. Symlinks or entries resolving outside the workspace are reported as `symlink`. |
| `read_file` | Required `path` (string) | Reads a UTF-8 text file up to 1,000,000 bytes (1 MB). Binary, non-UTF-8, oversized, or unreadable files are rejected. |
| `search_files` | Required non-blank `query` (string); optional `path` (string; defaults to `.`) | Searches case-insensitively. Skips symlinks and files that are binary, non-UTF-8, or over 1 MB. Returns at most 100 matching lines; each returned line is limited to 500 characters. |
| `write_file` | Required `path` (string) and `content` (string) | Writes UTF-8 text up to 1,000,000 bytes (1 MB). Creates missing parent directories and overwrites an existing file at that path. The destination must remain within the workspace. Returns `{"success":true,"path":"<workspace-relative-path>"}` on success. |

Tool argument objects reject unexpected keys. The agent has no delete, shell, or browser tools. **There is no centralized permission manager or user approval workflow:** the model can invoke `write_file` without confirmation, so it may create directories or overwrite files directly. The workspace boundary is not a substitute for action approval.

Example:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat `
  -ContentType "application/json" -Body '{"message":"Hello"}'
```

Configuration is documented in [README.md](./README.md). Provider-specific function-calling formats are normalized behind a shared provider interface; the API and agent/tool behavior are unchanged when switching providers.
