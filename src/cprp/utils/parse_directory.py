import os

import pyperclip

from .get_content_of_files import get_content_of_file, get_list_of_content_files
from .gitignore_parser import ScopedGitignoreParser
from .scan_directory import scan_directory
from .to_tree import directory_to_tree


def find_gitignore_files(directory: str) -> list:
    """Find inherited rules up to the nearest Git repository boundary."""
    directory = os.path.abspath(directory)
    ancestors = [directory]
    current = directory
    while not os.path.exists(os.path.join(current, ".git")):
        parent = os.path.dirname(current)
        if parent == current:
            # Outside a repository, only inherit from the selected root.
            ancestors = [directory]
            break
        ancestors.append(parent)
        current = parent
    return [
        os.path.join(parent, ".gitignore")
        for parent in reversed(ancestors)
        if os.path.isfile(os.path.join(parent, ".gitignore"))
    ]


def parse_directory(directory, tree_only: bool = False, follow_symlinks: bool = True):
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The specified directory does not exist: {directory}")
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"The specified path is not a directory: {directory}")

    package_dir = os.path.dirname(os.path.abspath(__file__))
    default_ignores_path = os.path.join(package_dir, "default.gitignore")
    parser = ScopedGitignoreParser(directory).with_file(directory, default_ignores_path)
    for ignore_file in find_gitignore_files(directory):
        if os.path.dirname(ignore_file) != os.path.abspath(directory):
            if follow_symlinks or not os.path.islink(ignore_file):
                parser = parser.with_file(os.path.dirname(ignore_file), ignore_file)

    directory_breakdown = scan_directory(directory, parser, follow_symlinks=follow_symlinks)
    tree = directory_to_tree(directory_breakdown)
    tree_structure = f"# DIRECTORY STRUCTURE\n\n{tree}\n"

    if tree_only:
        output_string = tree_structure
    else:
        content_string = "\n\n"
        _, contents = get_list_of_content_files(directory_breakdown)
        root_path = directory_breakdown["path"]

        for item in contents:
            relative_path = os.path.relpath(item["path"], root_path).replace(os.sep, "/")
            content_string += f"## {relative_path}\n"
            content_string += get_content_of_file(item["path"]) + "\n\n"

        output_string = tree_structure + content_string

    try:
        pyperclip.copy(output_string)
        print("\nCopied to clipboard!\n\n")
    except Exception as e:
        print(f"Could not copy to clipboard: {e}")

    print(output_string)
