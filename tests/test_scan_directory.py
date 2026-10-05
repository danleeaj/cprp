import tempfile
import unittest
from pathlib import Path

from cprp.utils.gitignore_parser import GitignoreParser
from cprp.utils.scan_directory import scan_directory


class ScanDirectoryTests(unittest.TestCase):
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

    def names(self, directory: dict) -> list:
        return [item["name"] for item in directory["contents"]]

    def child(self, directory: dict, name: str) -> dict:
        return next(item for item in directory["contents"] if item["name"] == name)

    def test_scans_recursively_in_alphabetical_order(self):
        self.write("z-last.txt")
        self.write("a-first.txt")
        self.write("middle/z-child.txt")
        self.write("middle/a-child.txt")

        result = scan_directory(str(self.root), GitignoreParser([]))

        self.assertEqual(self.names(result), ["a-first.txt", "middle", "z-last.txt"])
        self.assertEqual(
            self.names(self.child(result, "middle")),
            ["a-child.txt", "z-child.txt"],
        )

    def test_parser_is_optional(self):
        self.write("included.txt")

        result = scan_directory(str(self.root))

        self.assertEqual(self.names(result), ["included.txt"])

    def test_matches_nested_patterns_relative_to_original_root(self):
        self.write("generated/cache.txt")
        self.write("generated/keep.txt")
        ignore_file = self.write("rules.gitignore", "generated/cache.txt\n")

        result = scan_directory(
            str(self.root),
            GitignoreParser([str(ignore_file)]),
        )

        generated = self.child(result, "generated")
        self.assertEqual(self.names(generated), ["keep.txt"])

    def test_directory_patterns_prune_the_directory(self):
        self.write("build/output.txt")
        self.write("keep.txt")
        ignore_file = self.write("rules.gitignore", "build/\n")

        result = scan_directory(
            str(self.root),
            GitignoreParser([str(ignore_file)]),
        )

        self.assertEqual(self.names(result), ["keep.txt", "rules.gitignore"])


if __name__ == "__main__":
    unittest.main()
