import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from cprp.cli import app


class CliTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)

    def tearDown(self):
        self.temp_directory.cleanup()

    def assert_concise_error(self, result, expected_message: str):
        self.assertEqual(result.exit_code, 1)
        self.assertIn(f"Error: {expected_message}", result.output)
        self.assertNotIn("Traceback", result.output)

    def test_missing_directory_has_concise_error(self):
        missing_path = self.root / "missing"

        result = self.runner.invoke(app, [str(missing_path)])

        self.assert_concise_error(
            result,
            f"The specified directory does not exist: {missing_path}",
        )

    def test_file_path_has_concise_error(self):
        file_path = self.root / "file.txt"
        file_path.write_text("content", encoding="utf-8")

        result = self.runner.invoke(app, [str(file_path)])

        self.assert_concise_error(
            result,
            f"The specified path is not a directory: {file_path}",
        )

    def test_no_follow_symlinks_omits_links_in_full_and_tree_output(self):
        (self.root / "real").mkdir()
        (self.root / "real/keep.txt").write_text("keep-content")
        (self.root / "dir-alias").symlink_to("real", target_is_directory=True)
        (self.root / "file-alias").symlink_to("real/keep.txt")
        (self.root / "real/nested-alias").symlink_to("keep.txt")
        (self.root / "broken-alias").symlink_to("missing")
        for flags in (
            ["--no-follow-symlinks"],
            ["--no-follow-symlinks", "--tree-only"],
            ["-ns"],
            ["-ns", "--tree-only"],
        ):
            with self.subTest(flags=flags):
                with patch("cprp.utils.parse_directory.pyperclip.copy") as copy:
                    result = self.runner.invoke(app, [*flags, str(self.root)])
                self.assertEqual(result.exit_code, 0, result.output)
                output = copy.call_args.args[0]
                self.assertNotIn("alias", output)
                self.assertIn("keep.txt", output)
                if "--tree-only" not in flags:
                    self.assertIn("## real/keep.txt\nkeep-content", output)

    def test_default_still_follows_symlinks(self):
        (self.root / "target.txt").write_text("linked-content")
        (self.root / "alias.txt").symlink_to("target.txt")
        with patch("cprp.utils.parse_directory.pyperclip.copy") as copy:
            result = self.runner.invoke(app, [str(self.root)])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("## alias.txt\nlinked-content", copy.call_args.args[0])

    def test_filesystem_failure_has_concise_error(self):
        with patch(
            "cprp.cli.parse_directory",
            side_effect=PermissionError("permission denied"),
        ):
            result = self.runner.invoke(app, [str(self.root)])

        self.assert_concise_error(result, "permission denied")


if __name__ == "__main__":
    unittest.main()
