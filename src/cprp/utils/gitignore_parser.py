# The link for gitignore formatting for future reference:
# https://git-scm.com/docs/gitignore

# pathspec will be used for pattern matching:
# https://pypi.org/project/pathspec

import logging
import os
from typing import List

import pathspec

class GitignoreParser:
    def __init__(self, gitignore_paths: List[str]):
        self.patterns = self._compile_gitignore_paths_to_list(gitignore_paths)
        self.spec = pathspec.GitIgnoreSpec.from_lines(self.patterns)
        logging.info(f"{len(self.patterns)} pattern(s) identified.")

    def _compile_gitignore_paths_to_list(self, gitignore_paths: List[str]) -> List[str]:
        patterns = []
        for path in gitignore_paths:
            with open(path, "r", encoding="utf-8") as file:
                patterns.extend(file.readlines())
        return patterns

    def is_ignored(self, string_to_match: str) -> bool:
        """A method to check if the inputted string matches with any of the initiated gitignore patterns."""
        return self.spec.match_file(string_to_match)


class ScopedGitignoreParser:
    """Keep each ignore file's rules relative to its own directory."""

    def __init__(self, scan_root, layers=()):
        self.scan_root = os.path.abspath(scan_root)
        self.layers = tuple(layers)

    def with_file(self, directory, ignore_file):
        parser = GitignoreParser([ignore_file])
        return ScopedGitignoreParser(
            self.scan_root, self.layers + ((os.path.abspath(directory), parser.spec),)
        )

    def _matches(self, path, is_directory):
        ignored = False
        for scope, spec in self.layers:
            relative = os.path.relpath(path, scope).replace(os.sep, "/")
            if relative == "." or relative == ".." or relative.startswith("../"):
                continue
            if is_directory:
                relative += "/"
            # No match must preserve inherited rules; a negation overrides them.
            if any(p.include is not None and p.match_file(relative) for p in spec.patterns):
                ignored = spec.match_file(relative)
        return ignored

    def is_ignored(self, string_to_match):
        path = os.path.abspath(os.path.join(self.scan_root, string_to_match.rstrip("/")))
        parent = os.path.dirname(path)
        while parent != os.path.dirname(parent):
            if self._matches(parent, True):
                return True
            parent = os.path.dirname(parent)
        return self._matches(path, string_to_match.endswith("/"))
