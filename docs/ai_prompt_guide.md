# AI Prompt 指南：從 JSON 到 UI 程式碼

本指南提供如何引導 LLM (如 Claude 3.5 Sonnet 或 GPT-4) 讀取 `fig2json` 產出的資料並生成高品質 UI 程式碼的提示詞範例。

## 1. 基礎提示詞 (HTML/CSS)

當你將 `canvas.json` 的內容貼給 AI 時，建議使用以下結構：

```markdown
我將提供一個經過簡化的 Figma 設計稿 JSON。
請根據這個 JSON 的結構與屬性，生成一個響應式的 HTML 頁面與對應的 CSS：

1. **佈局**: 使用 Flexbox 或 CSS Grid 來對齊元素，參考 `absoluteBoundingBox` 與 `stackPrimaryAlignItems` 等屬性。
2. **樣式**: 將 `fillPaints` 轉為背景色，`fontName` 與 `fontSize` 轉為文字樣式。
3. **組件**: 識別具備 `name` 的組件並將其模組化。

這是設計稿資料：
[貼上 JSON 內容]
```

## 2. 進階提示詞 (Jetpack Compose / Kotlin)

針對 Android 開發，可以使用更具體的指令：

```markdown
請將以下 Figma JSON 轉換為 Jetpack Compose 程式碼：

- 將 `FRAME` 轉換為 `Box`, `Row` 或 `Column` (根據 `stackMode` 判斷)。
- 將 `TEXT` 轉換為 `Text` 組件，並映射 `textData.characters`。
- 顏色與圓角請參考 `fills` 與 `cornerRadius`。
- 請注意 `padding` 屬性的對應。

資料：
[貼上 JSON 內容]
```

## 3. 最佳實踐建議

*   **分段處理**: 如果設計稿非常大，請先提供 `components` 映射表，讓 AI 了解全域樣式，再分層級提供 `document` 的子節點。
*   **角色設定**: 在 Prompt 開頭加上「你是一位資深的 Android/前端工程師，擅長精準還原 Figma 設計」會顯著提升結果質量。
*   **坐標對齊**: 強調參考 `absoluteBoundingBox` 的 `x` 與 `y` 來處理元素間的相對位置。
