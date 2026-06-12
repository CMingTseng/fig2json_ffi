# JSON 產出體積與官方相容性分析報告

本報告針對 `fig2json` 產出的 `canvas.json` (約 120MB-138MB) 與 Figma 官方 REST API 產出的 `figma.json` (約 54MB-60MB) 進行深度比對與分析。

## 1. 核心發現：體積差異的真相 (Format vs. Content)

經過對原始資料（移除所有空白與縮排後）的計算，發現：
- **fig2json (canvas.json) 原始大小**: **36.7 MB**
- **Figma Official (figma.json) 原始大小**: **61.1 MB**

### 結論
`fig2json` 產出的**實際資料量僅為官方 API 的 60%**。使用者看到的 120MB 是因為產出的 JSON 進行了 **Pretty-print (縮排)**。官方提供的 JSON 通常是經過 Minified (壓縮) 或僅有極少縮排的。

> **建議**: 若要減少磁碟佔用或傳輸體積，請在執行時加上 `--compact` 參數。

---

## 2. 結構差異與改進空間

雖然實際資料量較小，但仍發現部分冗餘欄位與相容性問題：

### A. 殘留的內部資料 (vectorData)
- **現象**: 即使在 `lib.rs` 中啟用了 `remove_vector_data`，產出的 JSON 中仍存在大量 `vectorData` 欄位（約佔 2.8MB 原始體積）。
- **原因分析**: 
    1. 部分 `vectorData` 可能存在於 `components` 或 `componentSets` 中，而目前的 `remove_vector_data` 僅對 `document` 執行。
    2. `lib.rs` 中的轉換順序可能導致部分欄位在處理後被重新引入。
- **改善建議**: 將 `remove_vector_data` 移至 `output` 物件建立後執行，以覆蓋全域。

### B. 屬性名稱相容性 (fills/strokes)
- **現象**: 產出的 JSON 仍使用 `fillPaints` 與 `strokePaints`。
- **原因分析**: `rename_paints` 轉換雖然已在代碼中，但可能因為遞迴邏輯或執行順序未完全覆蓋 `document` 分支。
- **改善建議**: 確保 `rename_paints` 在所有結構化轉換完成後最後執行。

### C. 根節點冗餘
- **現象**: `blobs` 陣列雖然已空，但仍保留在 JSON 根部。
- **改善建議**: 取消 `lib.rs` 中 `remove_root_blobs` 的註釋。

---

## 3. 下一步優化行動方案 (Action Plan)

為了進一步逼近（甚至超越）官方 API 的精簡度，建議進行以下調整：

1.  **啟用更多精簡規則**: 在 `lib.rs` 中取消以下註釋：
    - `remove_guid_fields`: 移除內部 GUID，僅保留對齊後的 `id`。
    - `remove_default_blend_mode`: 移除預設的 "NORMAL"。
    - `remove_default_opacity`: 移除 `opacity: 1.0`。
    - `remove_default_visible`: 移除 `visible: true`。
2.  **全域轉換**: 將 `remove_vector_data` 與 `rename_paints` 從針對 `document` 調整為針對最終的 `output` 物件執行。
3.  **預設 Compact**: 考慮將 `--compact` 作為大規模處理時的建議選項，或將 Pretty-print 的縮排從 4 個空格改為 2 個（或不縮排）。

## 4. 驗證數據參考
| 檔案 | 磁碟大小 (Pretty) | 原始資料量 (Minified) | 備註 |
| :--- | :--- | :--- | :--- |
| `figma.json` (Official) | 54 MB | 61.1 MB | 官方原始資料較大但無縮排 |
| `canvas.json` (fig2json) | 138 MB | 36.7 MB | 資料極精簡但因縮排膨脹 |
