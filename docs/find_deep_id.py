import json
import sys

def find_long_id(node):
    if ';' in node.get('id', '') and node.get('id', '').count(';') > 1:
        return node.get('id')
    for child in node.get('children', []):
        res = find_long_id(child)
        if res: return res
    return None

if __name__ == "__main__":
    file_path = "/fig/figma.json"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
    try:
        with open(file_path, 'r') as f:
            d = json.load(f)
            print('Deep ID example:', find_long_id(d['document']))
    except Exception as e:
        print(f"Error: {e}")
