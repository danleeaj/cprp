import logging
import os
from typing import Optional

from .gitignore_parser import GitignoreParser


def scan_directory(
    directory_path: str,
    parser: Optional[GitignoreParser] = None,
    base_path: Optional[str] = None,
):
    """Scans directory and returns its contents as a dictionary.
    """

    if base_path is None:
        base_path = os.path.abspath(directory_path)

    logging.info(f"Scanning {directory_path}")

    base_directory = {
        "type": "directory",
        "name": os.path.basename(os.path.normpath(directory_path)),
        "path": os.path.abspath(directory_path),
        "contents": []
    }

    for item in sorted(os.listdir(directory_path)):
        item_path = os.path.join(directory_path, item)
        absolute_path = os.path.abspath(item_path)
        relative_path = os.path.relpath(absolute_path, base_path).replace(os.sep, "/")
        is_directory = os.path.isdir(item_path)
        path_to_match = f"{relative_path}/" if is_directory else relative_path
        is_ignored = parser.is_ignored(path_to_match) if parser else False

        logging.debug(f"Checking: {relative_path}, is_ignored: {is_ignored}")

        if is_ignored:
            continue

        if is_directory:
            subdirectory_items = scan_directory(item_path, parser, base_path)
            base_directory["contents"].append(subdirectory_items)
        else:
            file_info = {
                "type": "file",
                "name": item,
                "path": absolute_path,
            }
            base_directory["contents"].append(file_info)

    return base_directory
