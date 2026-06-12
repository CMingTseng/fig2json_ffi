# Figma 官方 API vs. fig2json 缺失數據分析報告

本文件詳細分析了為何 `fig2json` 產出的 JSON 體積遠小於官方 REST API 的原因，並指出了目前的結構性缺失。

## 1. 核心發現：節點數量的巨大差異

經由 `count_nodes.py` 分析發現，官方 JSON 與 `fig2json` 產出在節點數量上有極大落差：
- **Figma Official (figma.json)**: **52,094** 個節點
- **fig2json (canvas.json)**: **27,935** 個節點

**結論**: `fig2json` 缺失了約 **46%** 的節點數據。這也是產出檔案體積較小的主要原因（而非單純的優化）。

## 2. 缺失原因分析 (Root Causes)

### A. Instance 未展開 (Instance Expansion) - **關鍵原因**
- **現象**: 官方 REST API 會將所有 `INSTANCE` 節點展開，將 Master Component 的完整子樹注入到 Instance 中，並生成分號分隔的長 ID (例如 `I172:8070;130:6170`)。
- **fig2json 現況**: 僅保留 `INSTANCE` 節點本身及屬性覆蓋 (Overrides)，但不包含其內部的子節點樹。
- **影響**: 
    1. 節點數量大幅減少。
    2. 體積大幅縮減。
    3. **後果**: AI 讀取此 JSON 時，無法看到組件內部的具體結構（如按鈕內的文字、圖標），導致生成的代碼不完整。

### B. ComponentSet 識別錯誤
- **現象**: 官方 JSON 中有 50 個 `COMPONENT_SET` (Variant 容器)，而 `fig2json` 的 `componentSets` 地圖為空。
- **原因分析**: 在 Figma 內部資料中，Component Set 的類型標記為 `FRAME` 且帶有 `isStateGroup: true`。`fig2json` 目前僅根據 `type` 判斷，導致將其誤認為普通的 `FRAME`。
- **影響**: 無法正確提取 Variant 的元數據。

### C. 節點類型命名不對齊
- **現象**:
    - 官方 `COMPONENT` -> fig2json `SYMBOL`
    - 官方 `RECTANGLE` -> fig2json `ROUNDED_RECTANGLE`
- **影響**: 雖然資料在，但第三方工具 (MCP) 可能因為類型名稱不匹配而無法正確解析。

## 3. 改進建議 (Action Plan)

為了達成「官方格式高度相容」的目標，建議進行以下調整：

1.  **實作 Instance 遞迴展開**: 
    - 遍歷 `document` 樹時，遇到 `INSTANCE` 類型，需從 `components` 地圖中查找對應的 master tree 並深拷貝注入。
    - 需正確處理 ID 生成邏輯（分號組合）。
2.  **修正 ComponentSet 識別**:
    - 在 `extract_components_and_styles` 中，增加判斷 `isStateGroup == true` 的邏輯，並將其類型強制標記為 `COMPONENT_SET`。
3.  **類型名稱對齊**:
    - 在轉換階段將 `SYMBOL` 改名為 `COMPONENT`。
    - 將 `ROUNDED_RECTANGLE` 改名為 `RECTANGLE`（官方 API 使用 `cornerRadius` 屬性來區分圓角，而非獨立類型）。

## 4. 數據對比摘要 (Node Type Counts)
| 類型 | 官方數量 | fig2json 數量 | 狀態 |
| :--- | :--- | :--- | :--- |
| **總節點數** | **52,094** | **27,935** | **缺失嚴重** |
| VECTOR | 16,731 | 5,699 | 隨 Instance 展開後應會補足 |
| INSTANCE | 9,464 | 5,029 | 隨 Instance 展開後應會補足 |
| COMPONENT_SET | 50 | 0 | **識別錯誤 (誤認為 FRAME)** |
| COMPONENT | 2,202 | 2,202 | 命名為 SYMBOL，數量正確 |

---
*本報告揭示了目前體積縮減並非全然是「精簡優化」，而是「數據缺失」。若要供 AI 完整還原設計，必須解決 Instance 展開的問題。*
