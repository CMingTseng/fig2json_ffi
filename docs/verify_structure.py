import json
import sys

def get_structure(data, depth=0, max_depth=3):
    """遞迴提取 JSON 的結構摘要"""
    if depth > max_depth:
        return '...'
    
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if k == 'children' and isinstance(v, list) and len(v) > 0:
                result[k] = [get_structure(v[0], depth + 1, max_depth)]
            else:
                result[k] = get_structure(v, depth + 1, max_depth)
        return result
    elif isinstance(data, list):
        if len(data) > 0:
            return [get_structure(data[0], depth + 1, max_depth)]
        else:
            return []
    else:
        return type(data).__name__

if len(sys.argv) < 2:
    print("Usage: python3 verify_structure.py <json_file>")
    sys.exit(1)

try:
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
        print(f"Structure of {sys.argv[1]}:")
        print(json.dumps(get_structure(data), indent=2))
        print("\nRoot Keys:", list(data.keys()))
        if 'components' in data:
            print("Components count:", len(data['components']))
        if 'styles' in data:
            print("Styles count:", len(data['styles']))
except Exception as e:
    print(f"Error: {e}")
