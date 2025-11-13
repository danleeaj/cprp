import os
import logging
from .gitignore_parser import GitignoreParser

def scan_directory(directory_path: str, parser: GitignoreParser = None, root_path: str = None):
    """Scans directory and returns its contents as a dictionary.
    """

    # If root_path is not provided, this is the initial call, so set it
    if root_path is None:
        root_path = os.path.abspath(directory_path)

    logging.info(f"Scanning {directory_path}")

    base_directory = {
        "type": "directory",
        "name": os.path.basename(directory_path),
        "path": os.path.abspath(directory_path),
        "contents": []
    }

    try:

        directory_items = os.listdir(directory_path)

        for item in directory_items:

            # is_ignored = False
            item_path = os.path.join(directory_path, item)

            # Calculate relative path from root for proper gitignore matching
            relative_path = os.path.relpath(item_path, root_path)
            is_ignored = parser.is_ignored(relative_path)

            # Here is where we implement the checking.

            logging.debug(f"is_ignored: {is_ignored}")

            if not is_ignored:

                if os.path.isdir(item_path):
                    subdirectory_items = scan_directory(item_path, parser, root_path)
                    base_directory["contents"].append(subdirectory_items)
                else:
                    file_info = {
                        "type": "file",
                        "name": item,
                        "path": os.path.abspath(item_path),
                    }
                    base_directory["contents"].append(file_info)

    except Exception as e:
        print(e)

    return base_directory