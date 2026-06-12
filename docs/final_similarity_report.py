import json
import random
import sys

def collect_all_keys_deep(data, keys_set):
    if isinstance(data, dict):
        for k, v in data.items():
            keys_set.add(k)
            collect_all_keys_deep(v, keys_set)
    elif isinstance(data, list):
        for item in data:
            collect_all_keys_deep(item, keys_set)

def get_node_by_id(node, target_id):
    if not isinstance(node, dict): return None
    if node.get("id") == target_id: return node
    if "children" in node and isinstance(node["children"], list):
        for child in node["children"]:
            res = get_node_by_id(child, target_id)
            if res: return res
    return None

def get_all_node_ids(node, ids_list):
    if not isinstance(node, dict): return
    if "id" in node: ids_list.append(node["id"])
    if "children" in node and isinstance(node["children"], list):
        for child in node["children"]:
            get_all_node_ids(child, ids_list)

def compare_nodes_deep(n_off, n_fig):
    # Use deep key collection for the single node comparison too
    keys_off = set()
    keys_fig = set()
    collect_all_keys_deep({k:v for k,v in n_off.items() if k != "children"}, keys_off)
    collect_all_keys_deep({k:v for k,v in n_fig.items() if k != "children"}, keys_fig)
    
    common = keys_off.intersection(keys_fig)
    missing = keys_off - keys_fig
    extra = keys_fig - keys_off
    
    coverage = (len(common) / len(keys_off)) * 100 if keys_off else 100
    return coverage, sorted(list(missing)), sorted(list(extra))

if __name__ == "__main__":
    path_off = "/Users/neo.chang/Documents/AndroidStudioProjects/Fig2Json/fig/figma.json"
    path_fig = "/Users/neo.chang/Documents/AndroidStudioProjects/Fig2Json/temp_final_v8/canvas.json"
    
    with open(path_off, 'r') as f1, open(path_fig, 'r') as f2:
        data_off = json.load(f1)
        data_fig = json.load(f2)
        
    doc_off = data_off.get("document", {})
    doc_fig = data_fig.get("document", {})
    
    # 1. Overall Key Alignment
    keys_off = set()
    keys_fig = set()
    collect_all_keys_deep(doc_off, keys_off)
    collect_all_keys_deep(doc_fig, keys_fig)
    
    common_keys = keys_off.intersection(keys_fig)
    alignment_ratio = (len(common_keys) / len(keys_off)) * 100
    
    print(f"--- Global Alignment Report (Deep Key Inspection) ---")
    print(f"Official Unique Keys: {len(keys_off)}")
    print(f"Fig2Json Unique Keys: {len(keys_fig)}")
    print(f"Common Keys: {len(common_keys)}")
    print(f"Global Alignment Ratio: {alignment_ratio:.2f}%")
    print("-" * 30)

    # 2. Random 10 Node Comparison
    all_ids_off = []
    get_all_node_ids(doc_off, all_ids_off)
    
    # Filter IDs that exist in both files to see property coverage
    all_ids_fig = []
    get_all_node_ids(doc_fig, all_ids_fig)
    set_fig = set(all_ids_fig)
    
    common_ids = [idx for idx in all_ids_off if idx in set_fig and ";" in idx]
    sample_ids = random.sample(common_ids, min(10, len(common_ids)))
    
    print(f"--- Node Property Coverage (10 Random Common Nodes) ---")
    total_coverage = 0
    for nid in sample_ids:
        n_off = get_node_by_id(doc_off, nid)
        n_fig = get_node_by_id(doc_fig, nid)
        
        cov, missing, extra = compare_nodes_deep(n_off, n_fig)
        total_coverage += cov
        print(f"Node ID: {nid} ({n_off.get('type')}) -> Property Coverage: {cov:.2f}%")
        if missing:
            # Filter out known "hard to get" fields to see real missing data
            real_missing = [m for m in missing if m not in ['absoluteRenderBounds', 'scrollBehavior', 'layoutVersion']]
            if real_missing:
                print(f"  Significant Missing: {real_missing[:10]}...")
            
    print("-" * 30)
    print(f"Average Property Coverage: {total_coverage/len(sample_ids):.2f}%")
