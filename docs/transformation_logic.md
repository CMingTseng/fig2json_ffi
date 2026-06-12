# Fig2Json 轉換邏輯技術規格 (Technical Specifications)

本文件詳細紀錄 `fig2json` 工具中運用的 62 項核心轉換邏輯。這些邏輯旨在移除 Figma 內部的冗餘資料，將其轉換為對 AI (LLM) 友善且易於實作 UI (HTML/CSS/Compose) 的精簡格式。

## 核心轉換邏輯清單

| 編號 | 轉換名稱 (Transformation) | 功能描述 | 目的 |
| :--- | :--- | :--- | :--- |
| 1-8 | **解碼與基礎處理** | ZIP 解壓、Kiwi 解碼、Blob 替換、圖片 Hash 轉換。 | 基礎資料準備。 |
| 10 | `matrix_to_css` | 將 2D 矩陣轉換為 x, y, rotation, scale。 | 簡化幾何屬性，方便 CSS 實作。 |
| 11 | `colors_to_css` | 將 RGBA 對象轉換為 Hex 顏色字串 (#RRGGBB)。 | 統一顏色格式。 |
| 12 | `remove_text_glyphs` | 移除文字的向量字形資料 (glyphs)。 | 大幅減少檔案體積，AI 不需要向量路徑來理解文字。 |
| 13 | `simplify_enums` | 將 `{"value": "FRAME"}` 簡化為 `"FRAME"`。 | 提高資料可讀性，節省 Token。 |
| 14 | `remove_default_blend_mode` | 移除值為 "NORMAL" 的 blendMode。 | 移除預設值，精簡資料。 |
| 15 | `remove_guid_fields` | 移除 Figma 內部的 GUID 標識。 | 移除對 UI 實作無意義的內部 ID。 |
| 16 | `remove_edit_info` | 移除版本控制相關的編輯資訊 (editInfo)。 | 移除非設計屬性資料。 |
| 17 | `remove_phase` | 移除節點狀態資訊 (phase)。 | 移除 Figma 引擎運作狀態。 |
| 18 | `remove_geometry` | 移除詳細的幾何路徑 (fill/stroke geometry)。 | 除非是圖標，否則一般容器不需要路徑。 |
| 19-21| **文字版面優化** | 移除詳細的 Text Layout 與 Metadata。 | 僅保留關鍵的樣式與內容。 |
| 23-26| **文字屬性精簡** | 移除預設行高、字距、字體後綴。 | 簡化文字樣式對象。 |
| 27-28| **線條屬性優化** | 移除不相容 CSS 的邊框重量與描邊屬性。 | 確保輸出的屬性可被 CSS 直接引用。 |
| 30 | `remove_background` | 移除 `backgroundEnabled` 等冗餘屬性。 | 統一使用 fills 或 background 概念。 |
| 32 | `remove_internal_only` | 過濾掉標記為 `internalOnly: true` 的節點。 | 隱藏設計師不需要看到的輔助節點。 |
| 33-36| **預設值移除** | 移除 opacity: 1.0, visible: true, rotation: 0.0。 | 進一步精簡輸出。 |
| 37-41| **根部元數據清理** | 移除 document 屬性、guidPath、版本字串。 | 讓 JSON 結構僅聚焦於設計樹。 |
| 45 | `remove_corner_radii_ind` | 移除圓角獨立標記。 | 簡化矩形屬性。 |
| 48 | `remove_layout_aids` | 移除輔助線 (guides) 與網格 (layoutGrids)。 | 移除開發時不需要的輔助視覺元素。 |
| 49-50| **組件元數據優化** | 移除 `detachedSymbolID` 與 `overriddenSymbolID`。 | 簡化組件實例的資料結構。 |
| 53-54| **填寫/描邊優化** | 移除不可見的 paints 與空的 paint 陣列。 | 避免 AI 處理不生效的樣式。 |
| 55-58| **Auto Layout 優化** | 簡化 Stack (Auto Layout) 的間距與對齊屬性。 | 讓轉化為 CSS Flexbox 或 Compose Row/Column 更容易。 |
| 60 | `remove_type` | 移除節點類型欄位 (若不需要)。 | 進一步減少 Token 使用。 |
| 62 | `remove_empty_objects` | 移除所有空的 `{}` 對象。 | 最終的體積優化。 |

## 對開發者的意義
這些轉換不僅減少了傳輸體積，更重要的是**過濾掉了噪音**。在將此 JSON 提供給 LLM 時，AI 不會被 Figma 內部的引擎參數干擾，能更準確地識別出 CSS 的佈局意圖。
