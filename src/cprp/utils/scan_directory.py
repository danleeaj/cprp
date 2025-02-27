import os
import logging
from .gitignore_parser import GitignoreParser

def scan_directory(directory_path: str, parser: GitignoreParser = None):
    """Scans directory and returns its contents as a dictionary.
    """

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
            is_ignored = parser.is_ignored(item)

            # Here is where we implement the checking.

            logging.debug(f"is_ignored: {is_ignored}")

            if not is_ignored:

                if os.path.isdir(item_path):
                    subdirectory_items = scan_directory(item_path, parser)
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