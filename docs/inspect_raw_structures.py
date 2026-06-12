import json
import sys

def find_var_map(node):
    if 'variableConsumptionMap' in node and node['variableConsumptionMap'].get('entries'):
        return node['variableConsumptionMap']
    for child in node.get('children', []):
        res = find_var_map(child)
        if res: return res
    return None

def find_text_node(node):
    t = node.get('type')
    if isinstance(t, dict): t = t.get('value')
    if t == 'TEXT':
        return node
    for child in node.get('children', []):
        res = find_text_node(child)
        if res: return res
    return None

if __name__ == "__main__":
    file_path = '/Users/neo.chang/Documents/AndroidStudioProjects/Fig2Json/temp_extract/canvas.raw.json'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
    try:
        with open(file_path, 'r') as f:
            d = json.load(f)
            doc = d.get('document', {})
            
            print("--- Searching for variableConsumptionMap ---")
            vm = find_var_map(doc)
            if vm:
                print(json.dumps(vm, indent=2))
            else:
                print("Not found.")
                
            print("\n--- Searching for TEXT node structure ---")
            tn = find_text_node(doc)
            if tn:
                print(json.dumps({k: tn[k] for k in tn if k != 'children'}, indent=2))
            else:
                print("Not found.")
    except Exception as e:
        print(f"Error: {e}")
