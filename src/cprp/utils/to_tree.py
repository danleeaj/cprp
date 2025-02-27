def directory_content_to_tree(directory_dict, prefix="", is_last=True):
    """Convert a dictionary into a text representation of the directory.
    This function handles everything other than the first line.

    Args:
        directory_dict: Dictionary containing directory structure
        prefix: [FOR RECURSION] Prefix string for the current line
        is_last: If this item is the last in its parent's contents
    Returns:
        String representation of the directory structure
    """
    result = []
    name = directory_dict["name"]

    # Uses `-- if it's the last item in the directory, and |-- if not
    connector = "`-- " if is_last else "|-- "

    # If current file is a directory...
    if directory_dict["type"] == "directory":
        # Prefix is indent, if there is any;
        # Connector changes depending on whether it's the last item in the contents;
        # Name is the name of the file
        result.append(f"{prefix}{connector}{name}/")
        # Prepare the prefix for children
        new_prefix = prefix + ("    " if is_last else "|   ")
    else:
        result.append(f"{prefix}{connector}{name}")
        return "\n".join(result)

    # Process contents (if any)
    if "contents" in directory_dict and directory_dict["contents"]:
        contents = directory_dict["contents"]
        for i, item in enumerate(contents):
            is_last_item = (i == len(contents) - 1)
            result.append(directory_content_to_tree(item, new_prefix, is_last_item))

    return "\n".join(result)


def directory_to_tree(directory_dict):
    """Convert a nested directory dictionary into a tree-like string representation.

    Args:
        directory_dict: Dictionary containing directory structure
    Returns:
        String representation of the directory structure
    """
    root_name = directory_dict["name"]
    result = [f"{root_name}/"]

    if "contents" in directory_dict and directory_dict["contents"]:
        contents = directory_dict["contents"]
        for i, item in enumerate(contents):
            is_last = (i == len(contents) - 1)
            result.append(directory_content_to_tree(item, "", is_last))

    return "\n".join(result)