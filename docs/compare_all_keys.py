import json
import sys

def get_keys_recursive(data, keys):
    if isinstance(data, dict):
        for k, v in data.items():
            keys.add(k)
            get_keys_recursive(v, keys)
    elif isinstance(data, list):
        for item in data:
            get_keys_recursive(item, keys)

def main(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        d1 = json.load(f1)
        d2 = json.load(f2)
        
        keys1 = set()
        get_keys_recursive(d1.get('document', {}), keys1)
        
        keys2 = set()
        get_keys_recursive(d2.get('document', {}), keys2)
        
        only1 = keys1 - keys2
        only2 = keys2 - keys1
        
        print(f"Total Keys in Official Document: {len(keys1)}")
        print(f"Total Keys in fig2json Document: {len(keys2)}")
        print("\n--- Missing in fig2json ---")
        print(sorted(list(only1)))
        print("\n--- Extra in fig2json ---")
        print(sorted(list(only2)))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
