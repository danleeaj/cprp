def get_content_of_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except UnicodeDecodeError:
        return f"Cannot decode content of {path}"

def get_list_of_content_files(directory_dict: dict):

    paths = []
    contents = []
    stack = [directory_dict]

    while stack:
        current = stack.pop()

        if isinstance(current, dict) and "path" in current and "type" in current:
            paths.append(current["path"])
            if current["type"] == "file":
                contents.append(current)
            if "contents" in current and isinstance(current["contents"], list):
                for item in current["contents"]:
                    stack.append(item)

        elif isinstance(current, list):
            for item in current:
                stack.append(item)

    return paths, contents