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

    def test_filesystem_failure_has_concise_error(self):
        with patch(
            "cprp.cli.parse_directory",
            side_effect=PermissionError("permission denied"),
        ):
            result = self.runner.invoke(app, [str(self.root)])

        self.assert_concise_error(result, "permission denied")


if __name__ == "__main__":
    unittest.main()
