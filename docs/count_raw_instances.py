import json
import sys

def count_instances(node):
    t = node.get('type')
    if isinstance(t, dict): t = t.get('value')
    count = 1 if t == 'INSTANCE' else 0
    for child in node.get('children', []):
        count += count_instances(child)
    return count

if __name__ == "__main__":
    file_path = 'temp_extract/canvas.raw.json'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            print(f'Total INSTANCE nodes in {file_path}:', count_instances(data.get('document', {})))
    except Exception as e:
        print(f"Error: {e}")
