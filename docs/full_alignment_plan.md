# Fig2Json 完全對齊與數據修復計畫 (Full Alignment & Data Recovery Plan)

本計畫旨在解決目前 `fig2json` 產出 JSON 時嚴重的數據缺失問題（約 46% 節點缺失），以達成與 Figma 官方 REST API 的高度相容。

## 1. 核心缺失：Instance 展開 (Instance Expansion)

目前 `fig2json` 僅將 `INSTANCE` 節點作為單個節點處理，而官方 API 會將組件實例展開，注入 master component 的完整子節點樹。這是造成體積差異與 AI 解析不全的最主要原因。

### 實作步驟：
- [ ] **建立 Symbol 映射表**: 在 `build_tree` 階段，保留所有 `SYMBOL` (Component) 節點的完整結構。
- [ ] **遞迴展開邏輯**: 
    - 修改 `tree.rs` 中的 `build_node_tree`。
    - 當遇到 `INSTANCE` 類型時，根據其 `symbolData.symbolID` 找到對應的 `SYMBOL` 節點。
    - 複製該 `SYMBOL` 的所有子節點。
    - **ID 重新生成**: 展開後的子節點 ID 必須遵循官方格式：`[InstanceID];[ComponentChildID]`（例如 `1081:34;818:34`）。
    - **遞迴處理**: 若 Master Component 內部又包含其他 Instance，需遞迴展開。
- [ ] **屬性覆蓋 (Overrides)**: 處理 `symbolOverrides` 欄位，將實例特有的屬性（如文字內容、顏色、隱藏狀態）應用到展開後的子節點上。

## 2. 結構與命名完全對齊

- [x] **ComponentSet 識別**: (已完成) 將 `isStateGroup: true` 的 `FRAME` 正確識別為 `COMPONENT_SET`。
- [x] **類型命名對齊**: (已完成) 將 `SYMBOL` 映射為 `COMPONENT`，`ROUNDED_RECTANGLE` 映射為 `RECTANGLE`。
- [ ] **全域 metadata 補完**: 確保根部的 `components`, `styles`, `componentSets` 包含官方 API 所需的所有元數據（如 `key`, `remote`）。

## 3. 體積與性能優化

- [ ] **按需展開**: 考慮提供參數控制展開深度，以平衡 AI Context 限制與資料完整性。
- [ ] **移除內部冗餘**: 在展開完成後，執行最終的全域過濾，移除 `vectorData` 等機器專用資料。

## 4. 驗證流程

1.  **節點數量核對**: 使用 `count_nodes.py` 確保產出的節點總數接近官方的 52,000+。
2.  **結構路徑檢查**: 使用 `trace_node.py` 抽樣檢查 Instance 內部的子節點是否已正確注入且 ID 格式正確。
3.  **體積對比**: 期望展開後的 Indented JSON 體積會上升（接近 200MB+），但 Compact 版本應與官方 API 相當（約 60MB）。

---
*執行此計畫後，`fig2json` 將不再只是一個簡化工具，而是一個能完整還原設計語義的官方級別轉換器。*
