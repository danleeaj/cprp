def get_content_of_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return f"Cannot decode content of {path}"


def get_list_of_content_files(directory_dict: dict):
    paths = []
    contents = []

    def visit(current):
        if isinstance(current, list):
            for item in current:
                visit(item)
            return

        if isinstance(current, dict) and "path" in current and "type" in current:
            paths.append(current["path"])
            if current["type"] == "file":
                contents.append(current)
                return

            visit(current.get("contents", []))

    visit(directory_dict)

    return paths, contents
