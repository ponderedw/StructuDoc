def insert_path(tree, parts, path):
    node = tree
    for idx, part in enumerate(parts):
        found = next((
            child for child in node.get("children", [])
            if child["title"] == part),
                     None)
        if not found:
            found = {"title": part, "value": part
                     if idx+1 != len(parts) else path}
            node["children"] = node.get("children", [])
            node["children"].append(found)
        node = found


def build_tree(paths):
    tree = {"title": "root", "children": []}
    for path in paths:
        parts = path.strip().split("/")
        insert_path(tree, parts, path)
    return tree
