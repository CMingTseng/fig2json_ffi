import json
import sys

def has_key(node, key):
    if key in node: return True
    for child in node.get('children', []):
        if has_key(child, key): return True
    return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 check_key_existence.py <json_file> <key_name>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    key_to_check = sys.argv[2]
    
    try:
        with open(file_path, 'r') as f:
            d = json.load(f)
            print(f"Has '{key_to_check}' in document?", has_key(d.get('document', {}), key_to_check))
    except Exception as e:
        print(f"Error: {e}")
