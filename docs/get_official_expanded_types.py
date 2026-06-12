import json
import sys

def get_expanded_types(node, types):
    if ';' in node.get('id', ''):
        types.add(node.get('type'))
    for child in node.get('children', []):
        get_expanded_types(child, types)

if __name__ == "__main__":
    file_path = "/fig/figma.json"
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
    with open(file_path, 'r') as f:
        data = json.load(f)
        types = set()
        get_expanded_types(data.get('document', {}), types)
        print('Expanded node types:', sorted(list(types)))
