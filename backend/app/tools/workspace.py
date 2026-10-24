import os
from pathlib import Path, PurePosixPath, PureWindowsPath


MAX_TEXT_FILE_BYTES = 1_000_000
MAX_SEARCH_RESULTS = 100


class ToolError(Exception):
    pass


def _workspace_root(workspace: Path | str | None = None) -> Path:
    configured = workspace or os.getenv("CARAXES_WORKSPACE", "CARAXES_WORKSPACE")
    root = Path(configured)
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[2] / root
    try:
        root = root.resolve()
    except (OSError, RuntimeError):
        raise ToolError("CARAXES workspace path could not be resolved") from None
    if not root.is_dir():
        raise ToolError("CARAXES workspace directory does not exist")
    return root


def _resolve_path(path: str, workspace: Path | str | None = None) -> Path:
    if not isinstance(path, str) or "\0" in path:
        raise ToolError("Path must be a valid relative path")

    windows_path = PureWindowsPath(path)
    posix_path = PurePosixPath(path)
    parts = windows_path.parts if "\\" in path else posix_path.parts
    if windows_path.is_absolute() or windows_path.drive or posix_path.is_absolute() or ".." in parts or any(":" in part for part in parts):
        raise ToolError("Path must stay inside the CARAXES workspace")

    root = _workspace_root(workspace)
    try:
        resolved = (root / path).resolve()
    except (OSError, RuntimeError):
        raise ToolError("Workspace path could not be resolved") from None
    try:
        resolved.relative_to(root)
    except ValueError:
        raise ToolError("Path must stay inside the CARAXES workspace") from None
    return resolved


def _is_within_workspace(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return False
    except (OSError, RuntimeError):
        raise ToolError("Workspace path could not be resolved") from None
    return True


def _read_text_file(path: Path, skip_unsupported: bool = False) -> str | None:
    try:
        with path.open("rb") as file:
            content = file.read(MAX_TEXT_FILE_BYTES + 1)
    except OSError:
        raise ToolError("File is not a readable UTF-8 text file") from None
    if len(content) > MAX_TEXT_FILE_BYTES:
        if skip_unsupported:
            return None
        raise ToolError("Text file exceeds the 1 MB limit")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        if skip_unsupported:
            return None
        raise ToolError("File is not a readable UTF-8 text file") from None
    if "\0" in text:
        if skip_unsupported:
            return None
        raise ToolError("Binary files are not supported")
    return text


def list_directory(path: str = ".", workspace: Path | str | None = None) -> dict:
    directory = _resolve_path(path, workspace)
    if not directory.is_dir():
        raise ToolError("Directory does not exist")

    root = _workspace_root(workspace)
    entries = []
    for entry in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
        if entry.is_symlink() or not _is_within_workspace(entry, root):
            entry_type = "symlink"
        else:
            entry_type = "directory" if entry.is_dir() else "file" if entry.is_file() else "other"
        entries.append({
            "name": entry.name,
            "type": entry_type,
        })
    return {"path": path, "entries": entries}


def read_file(path: str, workspace: Path | str | None = None) -> dict:
    file_path = _resolve_path(path, workspace)
    if not file_path.is_file():
        raise ToolError("File does not exist")
    return {"path": path, "content": _read_text_file(file_path)}


def write_file(path: str, content: str, workspace: Path | str | None = None) -> dict:
    if not isinstance(content, str):
        raise ToolError("File content must be text")
    try:
        if len(content.encode("utf-8")) > MAX_TEXT_FILE_BYTES:
            raise ToolError("Text file exceeds the 1 MB write limit")
    except UnicodeEncodeError:
        raise ToolError("File content must be valid UTF-8 text") from None

    file_path = _resolve_path(path, workspace)
    root = _workspace_root(workspace)
    if file_path == root:
        raise ToolError("Path must name a file inside the CARAXES workspace")

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path = file_path.resolve()
        resolved_path.relative_to(root)
        if resolved_path.is_dir():
            raise ToolError("Path must name a file inside the CARAXES workspace")
        resolved_path.write_text(content, encoding="utf-8")
    except ToolError:
        raise
    except (OSError, RuntimeError, ValueError):
        raise ToolError("File could not be written inside the CARAXES workspace") from None

    return {"success": True, "path": resolved_path.relative_to(root).as_posix()}


def search_files(query: str, path: str = ".", workspace: Path | str | None = None) -> dict:
    if not isinstance(query, str) or not query.strip():
        raise ToolError("Search query must not be empty")

    directory = _resolve_path(path, workspace)
    if not directory.is_dir():
        raise ToolError("Directory does not exist")

    root = _workspace_root(workspace)
    matches = []

    def raise_walk_error(error: OSError) -> None:
        raise ToolError("Search could not access a workspace directory") from error

    for current, directories, filenames in os.walk(directory, followlinks=False, onerror=raise_walk_error):
        current_path = Path(current)
        directories[:] = [
            name for name in directories
            if not (current_path / name).is_symlink()
            and _is_within_workspace(current_path / name, root)
        ]
        for filename in sorted(filenames, key=str.casefold):
            candidate = current_path / filename
            if candidate.is_symlink() or not _is_within_workspace(candidate, root):
                continue
            try:
                relative_path = candidate.relative_to(root).as_posix()
                content = _read_text_file(candidate, skip_unsupported=True)
            except ValueError:
                continue
            if content is None:
                continue
            lines = content.splitlines()
            for line_number, line in enumerate(lines, start=1):
                if query.casefold() in line.casefold():
                    matches.append({
                        "path": relative_path,
                        "line": line[:500],
                        "line_number": line_number,
                    })
                    if len(matches) >= MAX_SEARCH_RESULTS:
                        return {"query": query, "path": path, "matches": matches}
    return {"query": query, "path": path, "matches": matches}


def execute_tool(name: str, arguments: object, workspace: Path | str | None = None) -> dict:
    if not isinstance(arguments, dict):
        raise ToolError("Tool arguments must be a JSON object")

    try:
        if name == "list_directory":
            if set(arguments) - {"path"}:
                raise ToolError("Invalid arguments for list_directory")
            return list_directory(arguments.get("path", "."), workspace)
        if name == "read_file":
            if set(arguments) != {"path"}:
                raise ToolError("Invalid arguments for read_file")
            return read_file(arguments["path"], workspace)
        if name == "write_file":
            if set(arguments) != {"path", "content"}:
                raise ToolError("Invalid arguments for write_file")
            return write_file(arguments["path"], arguments["content"], workspace)
        if name == "search_files":
            if set(arguments) - {"query", "path"} or "query" not in arguments:
                raise ToolError("Invalid arguments for search_files")
            return search_files(arguments["query"], arguments.get("path", "."), workspace)
    except ToolError:
        raise
    except OSError:
        raise ToolError("Workspace tool could not access the requested item") from None
    raise ToolError("Unknown workspace tool")
