# CARAXES Security

This document distinguishes safeguards present in the current backend from requirements that remain to be implemented. The current controls are useful boundaries, not a complete security or authorization system.

## Implemented safeguards

- Provider choice is explicit through `LLM_PROVIDER=nebius` or `LLM_PROVIDER=gemini`. Only the selected adapter is initialized; the application does not silently fall back.
- Provider keys and model names are read from environment variables: `NEBIUS_API_KEY` / `NEBIUS_MODEL` or `GEMINI_API_KEY` / `GEMINI_MODEL`. Keep secrets in the ignored `backend\.env`; never commit them or place them in source, logs, workspace files, or API responses.
- Provider exceptions are normalized so raw SDK errors and credential values are not returned by the chat API.
- The agent exposes only `list_directory`, `read_file`, `search_files`, and `write_file`. There are no shell, arbitrary code execution, delete, browser, or general operating-system tools.
- Workspace tools operate within `CARAXES_WORKSPACE`. Absolute paths, traversal, and paths resolving outside the configured root are rejected. The implementation checks symlinks and does not follow them during search.
- Read and search operations accept UTF-8 text files up to 1 MB; search returns at most 100 matching lines. Writes accept UTF-8 text up to 1 MB. Tool execution is bounded to three tool-call rounds and three tool calls per round.
- Tool schemas disallow additional properties, and the dispatcher checks the allowed argument keys for each tool. This is not a comprehensive schema validator for all value types or security policy.

## Current limitations and privacy risks

- `write_file` is available to the model and writes directly inside the workspace. It may create parent directories and overwrite files; there is no centralized permission manager, explicit user approval, or confirmation step.
- Path containment checks address traversal and symlink escapes at validation time, but the code does not guarantee protection against filesystem race conditions.
- There is no meaningful tool-action audit log, user cancellation mechanism, or post-action verification framework.
- No application-level timeout or general resource-limit policy is implemented for model and tool operations beyond the bounded tool rounds and file/search limits described above.
- The chat API sends user messages to the selected remote provider. If a workspace tool reads or searches private document content, that content is returned to the model as tool output and can be sent to the provider as part of the conversation. The current API has no pre-transfer privacy disclosure or consent workflow. Do not process private documents unless the user understands and accepts the selected provider's data handling terms.
- Never expose secrets to the LLM. Do not place credentials or other sensitive material in the workspace; workspace content is not filtered for secrets before being returned to the model.
- Neither Nebius nor Gemini is guaranteed to be free. Users must review the provider's current pricing, account access, and data-processing terms.

## Requirements before expanding actions

- LLM output must never authorize its own actions. A centralized, least-privilege permission manager must decide whether an operation is allowed.
- Destructive and sensitive operations must require explicit user approval. Approval must be attributable to the user and scoped to the requested action.
- Strict tool schemas and all arguments must be validated at the execution boundary, not trusted because the model or provider supplied them.
- Filesystem access must remain within explicitly approved workspaces. Design for path traversal, symlink escape, and race-condition attacks, including atomic or handle-based operations where appropriate.
- Do not add unrestricted shell execution or arbitrary code execution. Use narrowly scoped, auditable capabilities.
- Apply explicit timeouts and resource limits to model calls, tools, file processing, and automation.
- Record meaningful tool actions in audit logs while avoiding secret exposure; support cancellation and verify important actions before reporting success.
- Clearly disclose when private documents or other user data will be sent to a cloud model, and obtain consent before transfer.
- Keep credentials out of prompts and model-visible tool output. Keep secrets in local configuration and never commit them.

These are future requirements unless specifically identified as implemented above. A permission manager, approval workflow, comprehensive validation, audit log, cancellation, action verification, and complete race-condition defenses do not currently exist.
