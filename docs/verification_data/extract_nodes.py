import json, random, sys
from collections import Counter, defaultdict

PATH = '/sessions/determined-clever-thompson/mnt/other/WawelEmlYBJ5sCIOQwycSJ_from_figma.json'

with open(PATH) as f:
    data = json.load(f)

all_nodes = []

def walk(node, depth=0):
    if not isinstance(node, dict):
        return
    all_nodes.append(node)
    children = node.get('children')
    if isinstance(children, list):
        for c in children:
            walk(c, depth+1)

walk(data['document'])

print('Total nodes (document tree):', len(all_nodes))

type_counter = Counter()
key_counter = Counter()
key_by_type = defaultdict(Counter)

for n in all_nodes:
    t = n.get('type', 'UNKNOWN')
    type_counter[t] += 1
    for k in n.keys():
        key_counter[k] += 1
        key_by_type[t][k] += 1

print('\n--- Node type distribution (top 30) ---')
for t, c in type_counter.most_common(30):
    print(f'{t:30s} {c}')

print('\n--- All distinct node-level keys seen across all nodes (with frequency) ---')
for k, c in key_counter.most_common():
    print(f'{k:35s} {c}')

# Save full node list (id + type + keys) for later random sampling, to a json for reuse
out = {
    'total_nodes': len(all_nodes),
    'type_distribution': dict(type_counter),
    'key_frequency': dict(key_counter),
}
with open('/sessions/determined-clever-thompson/mnt/outputs/official_stats.json', 'w') as f:
    json.dump(out, f, indent=2)

# Save the flattened node list itself (id, type, keys only - to keep file small) for sampling reuse
slim = [{'id': n.get('id'), 'type': n.get('type'), 'name': n.get('name'), 'keys': sorted(n.keys())} for n in all_nodes]
with open('/sessions/determined-clever-thompson/mnt/outputs/official_nodes_slim.json', 'w') as f:
    json.dump(slim, f)

print('\nSaved official_stats.json and official_nodes_slim.json')
