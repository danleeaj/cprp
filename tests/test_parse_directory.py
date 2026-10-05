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

    def test_nested_rules_are_scoped_and_override_parent_rules(self):
        self.write(".gitignore", "*.log\n")
        self.write("a/.gitignore", "!keep.log\n/local.txt\ncache/\n")
        self.write("a/deep/.gitignore", "!deep.log\n")
        excluded = ["a/drop.log", "a/local.txt", "a/cache/data.txt", "b/keep.log"]
        included = ["a/keep.log", "a/deep/deep.log", "a/deep/local.txt", "b/local.txt"]
        for path in excluded + included:
            self.write(path, "payload:" + path)
        with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
            with redirect_stdout(io.StringIO()):
                parse_directory(str(self.root))
        output = self.copied_output(copy_mock)
        for path in excluded:
            self.assertNotIn("payload:" + path, output)
        for path in included:
            self.assertIn("## " + path + "\npayload:" + path, output)

    def test_subfolder_inherits_rules_to_nearest_repository_boundary(self):
        self.write(".gitignore", "*.log\n/sub/root-only.txt\n")
        (self.root / ".git").mkdir()
        self.write("sub/.gitignore", "!keep.log\n")
        self.write("sub/keep.log", "keep-payload")
        self.write("sub/drop.log", "drop-payload")
        self.write("sub/root-only.txt", "root-payload")
        with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
            with redirect_stdout(io.StringIO()):
                parse_directory(str(self.root / "sub"))
        output = self.copied_output(copy_mock)
        self.assertIn("keep-payload", output)
        self.assertNotIn("drop-payload", output)
        self.assertNotIn("root-payload", output)
        self.write("sub/.git", "gitdir: elsewhere\n")
        with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
            with redirect_stdout(io.StringIO()):
                parse_directory(str(self.root / "sub"))
        self.assertIn("drop-payload", self.copied_output(copy_mock))

    def test_ignored_parent_cannot_be_reincluded_by_nested_rules(self):
        (self.root / ".git").mkdir()
        self.write(".gitignore", "excluded/\n")
        self.write("excluded/.gitignore", "!keep.txt\n")
        self.write("excluded/keep.txt", "excluded-payload")
        for root in (self.root, self.root / "excluded"):
            with self.subTest(root=root):
                with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
                    with redirect_stdout(io.StringIO()):
                        parse_directory(str(root))
                self.assertNotIn("excluded-payload", self.copied_output(copy_mock))

    def test_nested_rules_apply_inside_followed_directory_links(self):
        with tempfile.TemporaryDirectory() as external:
            target = Path(external)
            (target / ".gitignore").write_text("drop.txt\n")
            (target / "drop.txt").write_text("drop-payload")
            (target / "keep.txt").write_text("keep-payload")
            (self.root / "linked").symlink_to(target, target_is_directory=True)
            with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
                with redirect_stdout(io.StringIO()):
                    parse_directory(str(self.root))
            output = self.copied_output(copy_mock)
            self.assertIn("## linked/keep.txt\nkeep-payload", output)
            self.assertNotIn("drop-payload", output)

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

    def test_broken_link_warns_and_other_files_are_copied(self):
        self.write("keep.txt", "keep-content")
        (self.root / "broken").symlink_to("missing.txt")

        with self.assertLogs(level="WARNING") as logs:
            with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
                with redirect_stdout(io.StringIO()):
                    parse_directory(str(self.root))

        self.assertIn("broken", "\n".join(logs.output))
        output = self.copied_output(copy_mock)
        self.assertIn("keep-content", output)
        self.assertNotIn("broken", output)

    def test_directory_links_are_followed_but_ancestor_loops_stop(self):
        self.write("keep.txt", "keep-content")
        (self.root / "loop").symlink_to(".", target_is_directory=True)
        with tempfile.TemporaryDirectory() as external:
            Path(external, "outside.txt").write_text("outside-content", encoding="utf-8")
            (self.root / "external").symlink_to(external, target_is_directory=True)
            for tree_only in (False, True):
                with self.subTest(tree_only=tree_only):
                    with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
                        with redirect_stdout(io.StringIO()):
                            parse_directory(str(self.root), tree_only=tree_only)
                    output = self.copied_output(copy_mock)
                    self.assertIn("loop/", output)
                    self.assertIn("external/", output)
                    self.assertIn("outside.txt", output)
                    self.assertNotIn("not followed", output)
                    self.assertNotIn("## loop", output)
                    if not tree_only:
                        self.assertIn("keep-content", output)
                        self.assertIn("## external/outside.txt\noutside-content", output)

    def test_directory_link_aliases_are_each_scanned_with_ignore_rules(self):
        self.write(".gitignore", "ignored/\n*/drop.txt\n")
        self.write("target/keep.txt", "keep-content")
        self.write("target/drop.txt", "drop-content")
        for name in ("alias-a", "alias-b", "ignored"):
            (self.root / name).symlink_to("target", target_is_directory=True)
        with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
            with redirect_stdout(io.StringIO()):
                parse_directory(str(self.root))
        output = self.copied_output(copy_mock)
        for name in ("alias-a", "alias-b", "target"):
            self.assertIn(f"## {name}/keep.txt\nkeep-content", output)
        self.assertNotIn("## ignored/", output)
        self.assertNotIn("-- ignored/", output)
        self.assertNotIn("drop-content", output)

    def test_ignored_broken_link_is_skipped_without_warning(self):
        self.write(".gitignore", "broken\n")
        (self.root / "broken").symlink_to("missing.txt")
        with patch("cprp.utils.scan_directory.logging.warning") as warning:
            with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
                with redirect_stdout(io.StringIO()):
                    parse_directory(str(self.root))
        warning.assert_not_called()
        self.copied_output(copy_mock)

    def test_valid_file_link_still_copies_contents(self):
        self.write("original.txt", "linked-content")
        (self.root / "alias.txt").symlink_to("original.txt")
        with patch("cprp.utils.parse_directory.pyperclip.copy") as copy_mock:
            with redirect_stdout(io.StringIO()):
                parse_directory(str(self.root))
        self.assertIn("## alias.txt\nlinked-content", self.copied_output(copy_mock))

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
