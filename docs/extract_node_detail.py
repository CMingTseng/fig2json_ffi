import json

file_path = "/fig/figma.json"
target_id = "16815:6293"

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
        # Only print the node itself without children to keep it small
        node_copy = {k: v for k, v in node.items() if k != "children"}
        print(json.dumps(node_copy, indent=2, ensure_ascii=False))
        
        # Check for boundVariables
        if "boundVariables" in node:
            print("\nBound Variables found:")
            print(json.dumps(node["boundVariables"], indent=2))
            
        # Check for colorVar (sometimes called this in custom exports, or boundVariables in official)
        if "colorVar" in str(node):
            print("\n'colorVar' string found in node data.")
            
    else:
        print(f"Node {target_id} not found.")

except Exception as e:
    print(f"Error: {e}")
