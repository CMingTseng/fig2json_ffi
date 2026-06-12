import json
import sys

def count_semicolons(node):
    count = 1 if ';' in node.get('id', '') else 0
    for child in node.get('children', []):
        count += count_semicolons(child)
    return count

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 count_semicolon_nodes.py <json_file>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
        print(f"Total nodes with semicolon IDs: {count_semicolons(data.get('document', {}))}")
