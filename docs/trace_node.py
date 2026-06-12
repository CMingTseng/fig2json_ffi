import json
import sys

def trace_node(node, name, path=[]):
    if name in node.get("name", ""):
        print(f"Found node: {node.get('name')}")
        print(f"  Type: {node.get('type')}")
        print(f"  ID: {node.get('id')}")
        print(f"  Path: {' -> '.join(path)}")
        return True
    
    for child in node.get("children", []):
        new_path = path + [f"{node.get('name')} ({node.get('type')})"]
        if trace_node(child, name, new_path):
            return True
    return False

d = json.load(open(sys.argv[1]))
trace_node(d['document'], sys.argv[2])
