# The link for gitignore formatting for future reference:
# https://git-scm.com/docs/gitignore

# pathspec will be used for pattern matching:
# https://pypi.org/project/pathspec

from typing import List
import logging
import pathspec

# TODO: Take all gitignores and compile them into a list

class GitignoreParser():
    def __init__(self, gitignore_paths: List[str]):
        self.patterns = self._compile_gitignore_paths_to_list(gitignore_paths)
        self.spec = pathspec.GitIgnoreSpec.from_lines(self.patterns)
        logging.info(f"{len(self.patterns)} pattern(s) identified.")

    def _compile_gitignore_paths_to_list(self, gitignore_paths: List[str]) -> List[str]:
        patterns = []
        for path in gitignore_paths:
            try:
                with open(path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception as e:
                logging.error(f"Error encountered while parsing gitignore file. Details: \n{e}")
        return patterns
    
    def is_ignored(self, string_to_match: str) -> bool:
        """A method to check if the inputted string matches with any of the initiated gitignore patterns."""
        try:
            ignore = self.spec.match_file(string_to_match)
        except Exception as e:
            print(f"Error encountered while matching file with glob pattern: {e}")
        return ignore