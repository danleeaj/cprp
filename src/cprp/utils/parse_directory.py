from .scan_directory import scan_directory
from .to_tree import directory_to_tree
from .get_content_of_files import get_list_of_content_files, get_content_of_file
from .gitignore_parser import GitignoreParser
import pyperclip
import os.path

def parse_directory(directory, tree_only: bool = False):

    if not os.path.exists(directory):
        raise FileNotFoundError(f"The specified directory does not exist: {directory}")
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"The specified path is not a directory: {directory}")

    package_dir = os.path.dirname(os.path.abspath(__file__))
    default_ignores_path = os.path.join(package_dir, "default.gitignore")
    parser = GitignoreParser([default_ignores_path])

    directory_breakdown = scan_directory(directory, parser)

    output_string = "# DIRECTORY STRUCTURE\n\n"

    tree = directory_to_tree(directory_breakdown)

    output_string += tree
    output_string += "\n"

    content_string = "\n\n"

    paths, contents = get_list_of_content_files(directory_breakdown)

    for item in contents:
        content_string += f"## {item['name']}\n"
        content_string += get_content_of_file(item['path']) + "\n\n"

    tree_structure = "" + output_string
    full_output = tree_structure + content_string

    if tree_only:
        output_string = tree_structure
    else:
        output_string = full_output

    try:
        pyperclip.copy(output_string)
        print("\nCopied to clipboard!\n\n")
    except Exception as e:
        print(f"Could not copy to clipboard: {e}")

    print(output_string)