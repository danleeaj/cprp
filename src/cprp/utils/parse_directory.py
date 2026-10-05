import os

import pyperclip

from .get_content_of_files import get_content_of_file, get_list_of_content_files
from .gitignore_parser import GitignoreParser
from .scan_directory import scan_directory
from .to_tree import directory_to_tree


def find_gitignore_files(directory: str) -> list:
    gitignore_paths = []

    root_gitignore = os.path.join(directory, ".gitignore")
    if os.path.isfile(root_gitignore):
        gitignore_paths.append(root_gitignore)

    return gitignore_paths


def parse_directory(directory, tree_only: bool = False):
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The specified directory does not exist: {directory}")
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"The specified path is not a directory: {directory}")

    package_dir = os.path.dirname(os.path.abspath(__file__))
    default_ignores_path = os.path.join(package_dir, "default.gitignore")
    gitignore_paths = [default_ignores_path] + find_gitignore_files(directory)
    parser = GitignoreParser(gitignore_paths)

    directory_breakdown = scan_directory(directory, parser)
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
