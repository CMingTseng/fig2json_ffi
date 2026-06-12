import json
import sys

def count_nodes(node):
    count = 1
    if "children" in node:
        for child in node["children"]:
            count += count_nodes(child)
    return count

def main(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            doc = data.get("document", {})
            total = count_nodes(doc)
            print(f"File: {file_path}")
            print(f"Total nodes in document: {total}")
            
            # Count by type
            types = {}
            def count_types(node):
                t = node.get("type", "UNKNOWN")
                types[t] = types.get(t, 0) + 1
                if "children" in node:
                    for child in node["children"]:
                        count_types(child)
            count_types(doc)
            print("Nodes by type:")
            for t, c in sorted(types.items(), key=lambda x: x[1], reverse=True):
                print(f"  {t}: {c}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 count_nodes.py <json_file>")
    else:
        main(sys.argv[1])
