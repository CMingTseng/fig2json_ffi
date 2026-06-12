import json
import sys
from collections import Counter

def analyze_json_size(data, path=""):
    sizes = Counter()
    
    if isinstance(data, dict):
        for k, v in data.items():
            current_path = f"{path}.{k}" if path else k
            serialized = json.dumps(v, ensure_ascii=False)
            sizes[current_path] += len(serialized)
            
            # Recursively analyze children but keep track of the key itself
            if k == "children" and isinstance(v, list):
                for i, child in enumerate(v):
                    # To avoid path explosion in deep trees, we aggregate by key name
                    sizes.update(analyze_json_size(child, f"{path}.children[*]"))
            elif isinstance(v, dict):
                sizes.update(analyze_json_size(v, current_path))
    return sizes

def main(file_path):
    print(f"Analyzing {file_path}...")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            sizes = analyze_json_size(data)
            
            print("\nTop 30 keys by total size (including their values):")
            for key, size in sizes.most_common(30):
                print(f"{size/1024/1024:10.2f} MB : {key}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_size.py <json_file>")
    else:
        main(sys.argv[1])
