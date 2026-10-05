import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from cprp.utils.parse_directory import find_gitignore_files, parse_directory


class ParseDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)

    def tearDown(self):
        self.temp_directory.cleanup()

    def write(self, relative_path: str, content: str = "content") -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def copied_output(self, copy_mock) -> str:
        copy_mock.assert_called_once()
        return copy_mock.call_args.args[0]

    def test_finds_only_an_existing_root_gitignore(self):
        self.assertEqual(find_gitignore_files(str(self.root)), [])
        gitignore = self.write(".gitignore", "*.log\n")

        self.assertEqual(find_gitignore_files(str(self.root)), [str(gitignore)])

    def test_applies_default_and_root_ignores_and_uses_relative_headings(self):
        self.write(".git/secret.txt", "secret-content")
        self.write(".gitignore", "generated/cache.txt\n")
        self.write("generated/cache.txt", "cache-content")
        self.write("generated/keep.txt", "keep-content")
        self.write("a/config.py", "a-content")
        self.write("b/config.py", "b-content")

        with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
            with redirect_stdout(io.StringIO()):
                parse_directory(str(self.root))

        output = self.copied_output(copy_mock)
        self.assertNotIn("secret-content", output)
        self.assertNotIn("cache-content", output)
        self.assertIn("keep-content", output)
        self.assertIn("## a/config.py", output)
        self.assertIn("## b/config.py", output)
        self.assertLess(output.index("## a/config.py"), output.index("## b/config.py"))
        self.assertLess(output.index("## b/config.py"), output.index("## generated/keep.txt"))

    def test_rejects_missing_paths_and_files_for_python_callers(self):
        missing_path = self.root / "missing"
        file_path = self.write("file.txt")

        with self.assertRaises(FileNotFoundError):
            parse_directory(str(missing_path))
        with self.assertRaises(NotADirectoryError):
            parse_directory(str(file_path))

    def test_tree_only_does_not_read_file_contents(self):
        self.write("file.txt", "content")

        with patch("cprp.utils.parse_directory.get_content_of_file") as read_mock:
            with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
                with redirect_stdout(io.StringIO()):
                    parse_directory(str(self.root), tree_only=True)

        read_mock.assert_not_called()
        output = self.copied_output(copy_mock)
        self.assertIn("file.txt", output)
        self.assertNotIn("## file.txt", output)

    def test_read_failure_does_not_copy_or_print_partial_success(self):
        self.write("file.txt", "content")
        terminal_output = io.StringIO()

        with patch(
            "cprp.utils.parse_directory.get_content_of_file",
            side_effect=OSError("cannot read file"),
        ):
            with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
                with self.assertRaisesRegex(OSError, "cannot read file"):
                    with redirect_stdout(terminal_output):
                        parse_directory(str(self.root))

        copy_mock.assert_not_called()
        self.assertEqual(terminal_output.getvalue(), "")

    def test_clipboard_failure_warns_and_still_prints_output(self):
        self.write("file.txt", "content")
        terminal_output = io.StringIO()

        with patch(
            "cprp.utils.parse_directory.pyperclip.copy",
            side_effect=OSError("clipboard unavailable"),
        ):
            with redirect_stdout(terminal_output):
                parse_directory(str(self.root))

        printed = terminal_output.getvalue()
        self.assertIn("Could not copy to clipboard: clipboard unavailable", printed)
        self.assertIn("## file.txt", printed)
        self.assertIn("content", printed)


if __name__ == "__main__":
    unittest.main()
