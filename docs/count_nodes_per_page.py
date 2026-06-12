import json
import sys

def count_nodes(node):
    count = 1
    if "children" in node:
        for child in node["children"]:
            count += count_nodes(child)
    return count

def main(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            doc = data.get("document", {})
            pages = doc.get("children", [])
            for page in pages:
                name = page.get("name", "Unnamed")
                total = count_nodes(page)
                print(f"{total:6} : {name}")
    except Exception as e:
        print(f"Error: {e}")

main(sys.argv[1])
