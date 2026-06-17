"""
比對 fig2json 實際轉換輸出 vs Figma 官方 REST API JSON。

用法：
    python3 compare_conversion.py <official.json> <converted.json>

預設檔名：
    official.json  = WawelEmlYBJ5sCIOQwycSJ_from_figma.json
    converted.json = canvas_output.json (fig2json 的輸出)

邏輯（對應使用者原始需求）：
    1. flatten 官方 json 的完整 document tree，取得「全部 node」列表（id -> node）
    2. random.seed(42) 從中抽 20 個節點
    3. 對每個抽到的節點，用 id 去 fig2json 輸出裡找對應節點，比較欄位覆蓋率
       （是否存在該欄位，不深究值是否完全相同，因為部分欄位如顏色/矩陣表示法
       本來就允許在對齊過程中轉換格式）
    4. absoluteRenderBounds 是 Figma 雲端排版引擎動態算出來的，靜態 .fig 檔案
       理論上無法重現，比對時排除，避免拉低覆蓋率造成誤判
    5. 印出每個節點的 coverage % 以及整體平均，並存成 compare_result.json

100% 覆蓋（排除 ENGINE_COMPUTED 後）= 該節點完全轉換成功。
"""
import json
import random
import sys

DEFAULT_OFFICIAL = 'WawelEmlYBJ5sCIOQwycSJ_from_figma.json'
DEFAULT_CONVERTED = 'canvas_output.json'
SEED = 42
SAMPLE_SIZE = 20

# Figma 雲端排版引擎動態計算出來的欄位，靜態 .fig 檔案無法重現，不計入缺漏
ENGINE_COMPUTED = {'absoluteRenderBounds'}


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def flatten(doc_root):
    nodes = {}

    def walk(node):
        if not isinstance(node, dict):
            return
        nid = node.get('id')
        if nid is not None:
            nodes[nid] = node
        children = node.get('children')
        if isinstance(children, list):
            for c in children:
                walk(c)

    walk(doc_root)
    return nodes


def main():
    official_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OFFICIAL
    converted_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CONVERTED

    official = load(official_path)
    converted = load(converted_path)

    official_nodes = flatten(official['document'])
    converted_nodes = flatten(converted['document'])

    print(f'官方 json 節點數: {len(official_nodes)}')
    print(f'fig2json 輸出節點數: {len(converted_nodes)}')

    all_ids = list(official_nodes.keys())
    random.seed(SEED)
    sample_ids = random.sample(all_ids, min(SAMPLE_SIZE, len(all_ids)))

    results = []
    for nid in sample_ids:
        onode = official_nodes[nid]
        cnode = converted_nodes.get(nid)
        if cnode is None:
            results.append({
                'id': nid,
                'type': onode.get('type'),
                'found': False,
                'coverage': 0.0,
                'missing_keys': sorted(set(onode.keys()) - ENGINE_COMPUTED),
            })
            continue
        okeys = set(onode.keys()) - ENGINE_COMPUTED
        ckeys = set(cnode.keys())
        present = okeys & ckeys
        missing = okeys - ckeys
        coverage = (len(present) / len(okeys) * 100) if okeys else 100.0
        results.append({
            'id': nid,
            'type': onode.get('type'),
            'found': True,
            'coverage': round(coverage, 1),
            'official_key_count': len(okeys),
            'matched_key_count': len(present),
            'missing_keys': sorted(missing),
        })

    found_count = sum(1 for r in results if r['found'])
    avg_coverage = sum(r['coverage'] for r in results) / len(results) if results else 0.0
    full_coverage_count = sum(1 for r in results if r['coverage'] >= 100.0)

    print(f'\n抽樣 {len(results)} 個節點 (seed={SEED})')
    print(f'ID 在輸出中找到: {found_count}/{len(results)}')
    print(f'平均欄位覆蓋率: {avg_coverage:.1f}%')
    print(f'100% 覆蓋節點數: {full_coverage_count}/{len(results)}')
    print()
    for r in results:
        missing_preview = r['missing_keys'][:6]
        print(f"{r['id']:45s} {str(r['type']):18s} found={str(r['found']):5s} "
              f"coverage={r['coverage']:5.1f}%  missing={missing_preview}")

    summary = {
        'official_total_nodes': len(official_nodes),
        'converted_total_nodes': len(converted_nodes),
        'sample_size': len(results),
        'found_in_output': found_count,
        'average_field_coverage_pct': round(avg_coverage, 1),
        'fully_covered_nodes': full_coverage_count,
    }
    with open('compare_result.json', 'w', encoding='utf-8') as f:
        json.dump({'summary': summary, 'details': results}, f, indent=2, ensure_ascii=False)
    print('\n已存 compare_result.json')


if __name__ == '__main__':
    main()
