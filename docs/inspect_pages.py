import json
import sys

def inspect_pages(file_path):
    print(f"Inspecting {file_path}")
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            doc = data.get("document", {})
            pages = doc.get("children", [])
            print(f"Total pages: {len(pages)}")
            for i, page in enumerate(pages):
                name = page.get("name", "Unnamed")
                child_count = len(page.get("children", []))
                print(f"  Page {i}: {name} ({child_count} direct children)")
    except Exception as e:
        print(f"Error: {e}")

inspect_pages(sys.argv[1])
