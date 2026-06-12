import json

file_path = "/json/figma.json"
ids_to_find = ["442:13506", "16794:3543", "16815:6293"]

def find_node(node, target_id):
    if node.get("id") == target_id:
        return node
    if "children" in node:
        for child in node["children"]:
            found = find_node(child, target_id)
            if found:
                return found
    return None

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    results = {}
    for tid in ids_to_find:
        # Search in document tree
        node = find_node(data.get("document", {}), tid)
        if node:
            results[tid] = node
        else:
            # Search in components if it exists (though usually it's in document)
            results[tid] = "Not found in document tree"

    print(json.dumps(results, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"Error: {e}")
