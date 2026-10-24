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

Sends one text message to Nebius Token Factory using the configured NVIDIA Nemotron model. The model may use the bounded, read-only workspace tools `list_directory`, `read_file`, and `search_files`.

**Request body:**

```json
{"message":"Hello"}
```

`message` must be a non-empty string and is trimmed. A missing, empty, or whitespace-only message is rejected by request validation (`422`).

**Response (`200`):**

```json
{"response":"<model-generated text>"}
```

Missing provider configuration returns `503`. A failed upstream request or empty model response returns `502`; secret values and raw provider errors are not returned.

Tool access is restricted to the existing `CARAXES_WORKSPACE` directory (default `backend/CARAXES_WORKSPACE`). Tool paths must be relative and remain within that directory. Read and search operations accept UTF-8 text files no larger than 1 MB; search skips non-text or oversized files and returns at most 100 matching lines. The agent executes at most three tool-call rounds. It does not create, modify, or delete workspace content, execute commands, or access the web.

Example:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat `
  -ContentType "application/json" -Body '{"message":"Hello"}'
```

Configuration is documented in [README.md](./README.md). The request uses Nebius Token Factory's OpenAI-compatible chat-completions API.
