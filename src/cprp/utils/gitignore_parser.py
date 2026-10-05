# The link for gitignore formatting for future reference:
# https://git-scm.com/docs/gitignore

# pathspec will be used for pattern matching:
# https://pypi.org/project/pathspec

import logging
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
