import logging
import os
from typing import FrozenSet, Optional, Tuple, Union

from .gitignore_parser import GitignoreParser, ScopedGitignoreParser


def scan_directory(
    directory_path: str,
    parser: Optional[Union[GitignoreParser, ScopedGitignoreParser]] = None,
    base_path: Optional[str] = None,
    _ancestors: FrozenSet[Tuple[int, int]] = frozenset(),
    follow_symlinks: bool = True,
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

    directory_stat = os.stat(directory_path)
    identity = (directory_stat.st_dev, directory_stat.st_ino)
    if identity in _ancestors:
        return base_directory
    ancestors = _ancestors | {identity}

    if isinstance(parser, ScopedGitignoreParser):
        relative_directory = os.path.relpath(directory_path, base_path).replace(os.sep, "/")
        if parser.is_ignored(relative_directory + "/"):
            return base_directory
        ignore_file = os.path.join(directory_path, ".gitignore")
        if os.path.isfile(ignore_file) and (follow_symlinks or not os.path.islink(ignore_file)):
            parser = parser.with_file(directory_path, ignore_file)

    for item in sorted(os.listdir(directory_path)):
        item_path = os.path.join(directory_path, item)
        if not follow_symlinks and os.path.islink(item_path):
            continue
        absolute_path = os.path.abspath(item_path)
        relative_path = os.path.relpath(absolute_path, base_path).replace(os.sep, "/")
        is_directory = os.path.isdir(item_path)
        path_to_match = f"{relative_path}/" if is_directory else relative_path
        is_ignored = parser.is_ignored(path_to_match) if parser else False

        logging.debug(f"Checking: {relative_path}, is_ignored: {is_ignored}")

        if is_ignored:
            continue

        if os.path.islink(item_path):
            if not os.path.exists(item_path):
                logging.warning("Skipping broken or unresolvable symbolic link: %s", relative_path)
                continue

        if is_directory:
            subdirectory_items = scan_directory(
                item_path, parser, base_path, ancestors, follow_symlinks=follow_symlinks
            )
            base_directory["contents"].append(subdirectory_items)
        else:
            file_info = {
                "type": "file",
                "name": item,
                "path": absolute_path,
            }
            base_directory["contents"].append(file_info)

    return base_directory
