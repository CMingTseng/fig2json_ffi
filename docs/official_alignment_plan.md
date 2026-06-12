# fig2json 官方格式對齊與優化計畫 (Official Alignment & Optimization Plan)

本文件紀錄了 `fig2json` 的開發策略，目標是先達成與 Figma 官方格式的高度相容，再逐步引入針對平台與 AI 的優化。

## 1. 開發階段策略 (Development Phases)

為了確保轉換後的數據能無縫對接現有工具（如 `figma-console-mcp`），開發將分為三個階段：

### 第一階段：官方格式高度相容 (High Compatibility - 優先目標)
- **目標**: 輸出 JSON 與 Figma REST API 結構一致，作為預設行為。
- **重點**: 
    - 恢復所有被過度優化的欄位（如顏色物件、預設屬性、佈局資訊）。
    - 計算並補足 `.fig` 內部缺少的官方欄位（如 `absoluteBoundingBox`）。
    - 建立根部全局映射表（`components`, `styles`）。
- **優點**: 產出的 JSON 可直接供現有的 MCP 工具使用，無需修改後端的 JS/TS 優化邏輯。

### 第二階段：平台定向優化 (Platform-Specific Optimization)
- **參數**: `--target <web|android|ios|flutter|compose>`
- **策略**: **「縮減而不破壞」**。
- **重點**:
    - 在維持官方結構的前提下，移除該平台絕對不需要的冗餘數據。
    - 針對目標平台進行單位換算（如 `dp`, `sp`, `rem`），但不強行改變官方標準欄位（可能以額外 metadata 形式存在）。
- **優點**: 減少傳輸體積，並為特定開發環境提供更精確的數值建議。

### 第三階段：AI 讀取友好化 (AI-Friendly Optimization)
- **參數**: `--ai`
- **策略**: **「極致精簡與語義強化」**。
- **重點**:
    - 移除所有 1.0/0.0 的預設值、將顏色 CSS 化 (Hex)。
    - 強制將複雜結構簡化為 AI 易讀的格式（可能破壞官方相容性）。
    - 強化佈局意圖（意圖描述大於物理座標）。
- **優點**: 極大化 Token 效率，適合直接輸入給 LLM 進行代碼生成。

---

## 2. 已完成的調整 (Completed Changes)

- [x] **ID 格式**: 轉換為 `"sessionID:localID"` 字串格式，並將 `guid` 重新命名為 `id`。
- [x] **節點類型**: 保留 `type` 欄位並簡化為字串值。
- [x] **顏色恢復**: 停止 CSS Hex 轉換，恢復為 `{"r", "g", "b", "a"}` 物件。
- [x] **屬性解封**: 停止移除 `visible`, `blendMode`, `opacity`, `rotation` 等預設屬性。

---

## 3. 待處理核心差異 (Core Discrepancies to Fix)

| 功能分類 | Figma 官方 API 特徵 | 優先順序 | 調整建議 |
| :--- | :--- | :--- | :--- |
| **絕對座標** | `absoluteBoundingBox` | **高** | 實作座標累加邏輯。研究顯示需透過遞迴遍歷樹狀結構，將父節點的 `transform` 矩陣與子節點累加，以計算出相對於 Page 的全局座標。 |
| **根部全局表** | `components`, `styles` 映射表 | **高** | 從 `.fig` 的元數據中提取 symbol 定義並匯總至根節點。 |
| **佈局屬性** | `scrollBehavior`, `constraints` | **中** | 停止在 `lib.rs` 中移除這些屬性。 |
| **變數系統** | `boundVariables` | **中** | 完整保留變數引用 (Variable Alias) 資訊。 |

---

## 4. 絕對座標計算研究 (Absolute Bounding Box Research)

### 核心邏輯
Figma 內部的座標系統是階層式的。每個節點的座標通常是相對於其父節點的。
- **資料來源**: 節點中的 `transform` (2D Affine Matrix) 或 `x`, `y` 欄位。
- **計算方法**: 
    1. 從 `CANVAS` (Page) 開始，Page 的座標視為 `(0, 0)`。
    2. 遍歷子節點時，將父節點的累計矩陣 $M_{parent}$ 與當前節點的相對矩陣 $M_{local}$ 相乘：$M_{global} = M_{parent} \times M_{local}$。
    3. `absoluteBoundingBox.x` 與 `y` 即為 $M_{global}$ 中的平移分量 ($tx, ty$)。
    4. `width` 與 `height` 則來自節點的 `size` 屬性。

### 實作計畫 (Phase 1 Task List)
- [ ] **Task 1.1**: 在 `tree.rs` 中實作遞迴座標累加器。
- [ ] **Task 1.2**: 確保 `absoluteBoundingBox` 被注入到每個節點。
- [ ] **Task 2.1**: 掃描 `nodeChanges` 中的 `SYMBOL` 與 `STYLE` 類型節點。
- [ ] **Task 2.2**: 在根節點建立 `components` 與 `styles` 映射表，對齊官方 API。
- [ ] **Task 3**: 調整 `lib.rs` 參數，預設關閉所有會破壞官方結構的 `remove_*` 步驟。

---

## 5. 參考資料
- 官方結構提取樣本: `/Users/neo.chang/Documents/AndroidStudioProjects/Fig2Json/json/figma.json`
- 目前轉換基準: `fig2json` 預設輸出應以此為目標。
