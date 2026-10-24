# CARAXES Agent Instructions

- Inspect existing code and relevant documentation before making changes.
- Work only on the requested task and one phase at a time; do not implement future phases.
- Reuse existing functionality and preserve unrelated behavior.
- Prefer the smallest correct implementation; avoid unnecessary code, dependencies, and abstractions.
- Test the requested behavior before stopping and report results accurately.
- Never hardcode, expose, or commit credentials; `.env` files must remain untracked.
- Do not use `eval` or `exec` for arbitrary execution, or give an LLM unrestricted shell/system access.
- Validate future tool inputs, require permission for dangerous actions, and verify important actions before reporting success.
- Use a feature branch, focused commit, push, pull request, and review; do not push directly to `main`.
- Stop after completing the requested task. Do not commit, push, merge, or create a PR unless explicitly asked.
