import json

file_path = "/json/figma.json"
target_id = "16794:3543"

def find_node(node, tid):
    if node.get("id") == tid:
        return node
    if "children" in node:
        for child in node["children"]:
            found = find_node(child, tid)
            if found:
                return found
    return None

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    node = find_node(data.get("document", {}), target_id)
    if node:
        node_copy = {k: v for k, v in node.items() if k != "children"}
        print(json.dumps(node_copy, indent=2, ensure_ascii=False))
    else:
        print(f"Node {target_id} not found.")

except Exception as e:
    print(f"Error: {e}")
