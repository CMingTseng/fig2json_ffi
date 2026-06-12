import json
import sys

def get_all_keys(data, prefix=""):
    """收集 JSON 中所有路徑的 Key"""
    keys = set()
    if isinstance(data, dict):
        for k, v in data.items():
            path = f"{prefix}.{k}" if prefix else k
            keys.add(path)
            # 對於大型陣列如 children，只檢查第一個元素以節省時間與 Context
            if k == "children" and isinstance(v, list) and len(v) > 0:
                keys.update(get_all_keys(v[0], path + "[0]"))
            elif not isinstance(v, list):
                keys.update(get_all_keys(v, path))
    return keys

def compare(file_official, file_fig2json):
    print(f"Comparing Official: {file_official}")
    print(f"With fig2json: {file_fig2json}\n")

    try:
        with open(file_official, 'r') as f1, open(file_fig2json, 'r') as f2:
            d1 = json.load(f1)
            d2 = json.load(f2)

            keys1 = get_all_keys(d1)
            keys2 = get_all_keys(d2)

            common = keys1.intersection(keys2)
            only_in_official = keys1 - keys2
            only_in_fig2json = keys2 - keys1

            print(f"--- Statistics ---")
            print(f"Common Keys: {len(common)}")
            print(f"Keys only in Official: {len(only_in_official)}")
            print(f"Keys only in fig2json: {len(only_in_fig2json)}")

            print(f"\n--- Missing in fig2json (Sample of first 20) ---")
            for k in sorted(list(only_in_official))[:20]:
                print(f"[-] {k}")

            print(f"\n--- Extra in fig2json (Sample of first 20) ---")
            for k in sorted(list(only_in_fig2json))[:20]:
                print(f"[+] {k}")

    except Exception as e:
        print(f"Error during comparison: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 compare_figma_jsons.py <official_json> <fig2json_output>")
    else:
        compare(sys.argv[1], sys.argv[2])
