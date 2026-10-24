import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.tools.workspace import (
    MAX_TEXT_FILE_BYTES,
    ToolError,
    execute_tool,
    list_directory,
    read_file,
    search_files,
    write_file,
)


class WorkspaceToolTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary_directory.name) / "workspace"
        self.workspace.mkdir()
        (self.workspace / "notes").mkdir()
        (self.workspace / "notes" / "welcome.txt").write_text("Caraxes can search this.", encoding="utf-8")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_list_directory_returns_workspace_entries(self):
        result = list_directory("notes", self.workspace)

        self.assertEqual(result["entries"], [{"name": "welcome.txt", "type": "file"}])

    @patch.dict("os.environ", {"CARAXES_WORKSPACE": "./CARAXES_WORKSPACE"})
    def test_default_workspace_is_configurable_from_backend(self):
        result = list_directory()

        self.assertIn(".gitkeep", {entry["name"] for entry in result["entries"]})

    def test_read_file_returns_utf8_content(self):
        result = read_file("notes/welcome.txt", self.workspace)

        self.assertEqual(result["content"], "Caraxes can search this.")

    def test_write_file_creates_file_inside_workspace(self):
        result = write_file("notes/new.txt", "Hello, CARAXES!", self.workspace)

        self.assertEqual(result, {"success": True, "path": "notes/new.txt"})
        self.assertEqual((self.workspace / "notes" / "new.txt").read_text(encoding="utf-8"), "Hello, CARAXES!")

    def test_write_file_creates_nested_parent_directories(self):
        result = write_file("projects/new/note.txt", "Nested.", self.workspace)

        self.assertEqual(result, {"success": True, "path": "projects/new/note.txt"})
        self.assertEqual((self.workspace / "projects" / "new" / "note.txt").read_text(encoding="utf-8"), "Nested.")

    def test_write_file_rejects_absolute_and_traversal_paths(self):
        invalid_paths = (
            str(self.workspace / "outside.txt"),
            "../outside.txt",
            "notes/../../outside.txt",
            r"..\outside.txt",
            r"notes\..\..\outside.txt",
            r"C:\outside.txt",
        )
        for path in invalid_paths:
            with self.subTest(path=path), self.assertRaises(ToolError):
                write_file(path, "not allowed", self.workspace)

    def test_write_file_rejects_oversized_content(self):
        with self.assertRaisesRegex(ToolError, "1 MB write limit"):
            write_file("large.txt", "x" * (MAX_TEXT_FILE_BYTES + 1), self.workspace)
        self.assertFalse((self.workspace / "large.txt").exists())

    def test_write_file_reports_filesystem_failures(self):
        with patch("app.tools.workspace.Path.write_text", side_effect=PermissionError):
            with self.assertRaisesRegex(ToolError, "could not be written"):
                write_file("notes/blocked.txt", "text", self.workspace)

    def test_write_file_rejects_symlink_escape_when_supported(self):
        outside = Path(self.temporary_directory.name) / "outside"
        outside.mkdir()
        link = self.workspace / "escape"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation is unavailable")

        with self.assertRaisesRegex(ToolError, "inside the CARAXES workspace"):
            write_file("escape/blocked.txt", "not allowed", self.workspace)
        self.assertFalse((outside / "blocked.txt").exists())

    def test_search_files_finds_case_insensitive_matches(self):
        result = search_files("CARAXES", workspace=self.workspace)

        self.assertEqual(result["matches"], [{
            "path": "notes/welcome.txt",
            "line": "Caraxes can search this.",
            "line_number": 1,
        }])

    def test_rejects_traversal_absolute_and_windows_paths(self):
        for path in ("../outside.txt", "notes/../../outside.txt", str(self.workspace / "notes" / "welcome.txt"), r"..\outside.txt", r"C:\outside.txt"):
            with self.subTest(path=path), self.assertRaises(ToolError):
                read_file(path, self.workspace)

    def test_rejects_unknown_tool_and_extra_arguments(self):
        with self.assertRaisesRegex(ToolError, "Unknown"):
            execute_tool("run_command", {}, self.workspace)
        with self.assertRaisesRegex(ToolError, "Invalid arguments"):
            execute_tool("read_file", {"path": "notes/welcome.txt", "extra": True}, self.workspace)

    def test_rejects_empty_search_and_binary_files(self):
        (self.workspace / "image.bin").write_bytes(b"\x00\x01")

        with self.assertRaisesRegex(ToolError, "must not be empty"):
            search_files(" ", workspace=self.workspace)
        with self.assertRaisesRegex(ToolError, "Binary"):
            read_file("image.bin", self.workspace)
        self.assertEqual(search_files("Caraxes", workspace=self.workspace)["matches"][0]["path"], "notes/welcome.txt")

    def test_rejects_oversized_text_reads(self):
        (self.workspace / "large.txt").write_bytes(b"x" * 1_000_001)

        with self.assertRaisesRegex(ToolError, "1 MB limit"):
            read_file("large.txt", self.workspace)

    def test_missing_workspace_is_not_created(self):
        missing = self.workspace.parent / "missing"

        with self.assertRaisesRegex(ToolError, "does not exist"):
            list_directory(".", missing)
        self.assertFalse(missing.exists())

    def test_rejects_symlink_escape_when_supported(self):
        outside = Path(self.temporary_directory.name) / "outside.txt"
        outside.write_text("secret", encoding="utf-8")
        link = self.workspace / "escape.txt"
        outside_directory = Path(self.temporary_directory.name) / "outside"
        outside_directory.mkdir()
        (outside_directory / "private.txt").write_text("secret Caraxes", encoding="utf-8")
        directory_link = self.workspace / "outside"
        try:
            link.symlink_to(outside)
            directory_link.symlink_to(outside_directory, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation is unavailable")

        with self.assertRaisesRegex(ToolError, "inside the CARAXES workspace"):
            read_file("escape.txt", self.workspace)
        self.assertFalse(search_files("secret", workspace=self.workspace)["matches"])


if __name__ == "__main__":
    unittest.main()
