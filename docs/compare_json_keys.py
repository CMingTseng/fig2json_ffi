import json
import sys

def collect_metadata(node, keys):
    for k in node.keys():
        keys.add(k)
    for child in node.get('children', []):
        collect_metadata(child, keys)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 compare_json_keys.py <file1.json> <file2.json>")
        sys.exit(1)
        
    with open(sys.argv[1], 'r') as f1, open(sys.argv[2], 'r') as f2:
        keys1, keys2 = set(), set()
        collect_metadata(json.load(f1).get('document', {}), keys1)
        collect_metadata(json.load(f2).get('document', {}), keys2)

        only_official = keys1 - keys2
        only_fig2json = keys2 - keys1
        print('--- Only in First File (Missing in Second) ---')
        print(sorted(list(only_official)))
        print('\n--- Only in Second File (Extra/Not Aligned) ---')
        print(sorted(list(only_fig2json)))
