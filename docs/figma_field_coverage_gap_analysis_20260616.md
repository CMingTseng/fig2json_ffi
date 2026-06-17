# Figma 官方欄位覆蓋率缺口分析（2026-06-16，純靜態分析）

## 背景

本分析使用兩個新增檔案：

- `SpayCardholderApp_20260615.fig`（41MB，目標專案 .fig 原始檔，位於 repo 外層 `other/` 目錄）
- `WawelEmlYBJ5sCIOQwycSJ_from_figma.json`（60MB，Figma 官方 REST API 匯出的對照基準，同樣位於 `other/` 目錄）

**重要限制**：本次分析環境（Cowork sandbox）沒有 Rust 編譯器（無 cargo/rustc，無 root，網路白名單擋掉 static.rust-lang.org / crates.io），因此**無法實際編譯執行 fig2json 來產生 `.fig` 的真實輸出**。本文件是針對官方 JSON 結構 + fig2json 原始碼本身做的純靜態比對，尚未做「真實轉換輸出 vs 官方」的端對端驗證。要完成端對端驗證，需要在有 Rust 工具鏈的環境（例如本機或 Claude Code）執行：

```
cargo run --release -- SpayCardholderApp_20260615.fig -o canvas.json
```

再用本目錄下 `verification_data/extract_nodes.py` 的方法對兩份 json 做節點抽樣比對。

## 官方 JSON 節點統計

`document` tree 總節點數：**58,063**

型別分布（前段）：

| type | count |
|---|---|
| VECTOR | 18,135 |
| FRAME | 14,262 |
| INSTANCE | 10,730 |
| TEXT | 9,968 |
| COMPONENT | 2,202 |
| RECTANGLE | 1,699 |
| GROUP | 395 |
| ELLIPSE | 394 |
| BOOLEAN_OPERATION | 162 |
| COMPONENT_SET | 50 |
| CANVAS | 37 |
| REGULAR_POLYGON | 15 |
| STAR | 8 |
| SECTION | 5 |
| DOCUMENT | 1 |

全部節點上出現過的 distinct 欄位名稱共 **97 個**（完整頻率清單見 `verification_data/official_stats.json`）。20 個隨機抽樣節點（`random.seed(42)`）已存於 `verification_data/sample20.json`，其中已確認多個 instance-expansion 產生的分號式 ID（例如 `I418:4337;230:4062;230:3921;230:3892;107:1496`），證實官方格式確實會展開 INSTANCE 節點的完整子樹。

## 欄位覆蓋率三層分類

針對官方 97 個欄位逐一 grep `fig2json/src`，並對照 `lib.rs` 實際呼叫的 pipeline，分成三層：

### 1. 目前 active pipeline 確實產出（約 24 個核心欄位）

來源：`lib.rs` 實際呼叫的模組 = `align_node_types` / `simplify_enums` / `rename_paints` / `align_fields` / `transform_guids_to_ids` / `rename_transform` / `remove_guid_fields` / `remove_internal_only_nodes` / `remove_vector_data` / `remove_detached_symbol_id` / `remove_overridden_symbol_id` / `remove_root_blobs` / `remove_text_glyphs` / `transform_image_hashes` / `tree::build_tree`。

涵蓋：`id`、`name`、`type`（含 SYMBOL→COMPONENT、ROUNDED_RECTANGLE→RECTANGLE 等對齊）、`children`、`absoluteBoundingBox`（僅 x/y/width/height，無 render bounds）、`layoutMode`、`itemSpacing`、`paddingLeft/Right/Top/Bottom`、`characters`、`style.fontFamily`/`fontPostScriptName`（部分）、`componentId`、`overrides`、`constraints`、`rectangleCornerRadii`、`clipsContent`、`boundVariables`、`backgroundColor`、`styles`、`interactions`、`layoutAlign`、`layoutGrow`，以及透過 `simplify_enums`/`rename_paints` 處理的 `blendMode`/`fills`/`strokes`/`strokeAlign` 等列舉與 paint 欄位。

### 2. 程式碼存在但目前**未被 lib.rs 呼叫**（dead code，約 17 個相關欄位受影響）

`transformations/` 下宣告了 63 個子模組，但 `lib.rs` 只呼叫上述 15 個。其餘大多是舊版「AI 友善激進精簡」邏輯的**移除類**函式（例如 `remove_stack_align_items`、`remove_text_layout_fields`、`transform_colors_to_css`、`transform_matrix_to_css`），這些函式被刻意註解掉並附註「為了 99% 對齊不要跑」。

**注意**：這些 dead code 幾乎全部是「移除欄位」邏輯，不是「新增官方欄位」邏輯。重新啟用它們**不會**讓輸出更接近官方格式，反而會讓輸出更精簡、偏離官方 schema。例如 `stack_align_items_removal.rs` 目前的設計是直接刪除 `stackPrimaryAlignItems`/`stackCounterAlignItems`，而不是改名成官方的 `primaryAxisAlignItems`/`counterAxisAlignItems`——這與舊文檔聲稱「Auto Layout 100% 對齊」有出入，是一個已用程式碼證實的落差。

### 3. 完全沒有任何程式碼處理（真正缺口，56 個欄位，佔 97 個官方欄位的 58%）

| 分類 | 欄位 |
|---|---|
| Auto Layout 次軸/新屬性 | `primaryAxisAlignItems`、`primaryAxisSizingMode`、`counterAxisAlignItems`、`counterAxisSizingMode`、`counterAxisAlignContent`、`counterAxisSpacing`、`layoutWrap`、`layoutSizingHorizontal`、`layoutSizingVertical`、`layoutPositioning`、`layoutVersion` |
| Grid Layout（全新功能） | `gridAutoTracks`、`gridChildHorizontalAlign`、`gridChildVerticalAlign`、`gridColumnAnchorIndex`、`gridColumnCount`、`gridColumnGap`、`gridColumnSpan`、`gridColumnsSizing`、`gridItemsPositioning`、`gridRowAnchorIndex`、`gridRowCount`、`gridRowGap`、`gridRowSpan`、`gridRowsSizing` |
| 文字進階 | `lineTypes`、`lineIndentations`、`characterStyleOverrides`、`styleOverrideTable` |
| 線條細節 | `strokeCap`、`strokeDashes`、`strokeMiterAngle`、`individualStrokeWeights`、`complexStrokeProperties` |
| Component Properties | `componentProperties`、`componentPropertyDefinitions`、`componentPropertyReferences` |
| Prototype 進階 | `prototypeDevice`、`prototypeStartNodeID`、`flowStartingPoints`、`transitionNodeID`、`transitionDuration`、`transitionEasing` |
| 節點旗標 | `isMask`、`isMaskOutline`、`maskType`、`isFixed`、`locked`、`sectionContentsHidden` |
| 其他 | `booleanOperation`、`arcData`、`minWidth`、`minHeight`、`preserveRatio`、`fillOverrideTable`、`scrollBehavior` |
| 結構性無法修復 | `absoluteRenderBounds`（Figma 雲端排版引擎動態計算結果，靜態 .fig 檔案無法推算，非程式錯誤） |

其中「Auto Layout 次軸」與「節點旗標」這兩類，原始 Kiwi 內部欄位（如 `stackPrimaryAlignItems`）目前沒有任何 pass 碰它們，理論上資料還留在輸出中、只是用內部命名，**改名成本應該不高**；Grid Layout、Component Properties、Prototype 進階則是完全新功能，需要從 Kiwi schema 重新研究欄位來源，工作量較大。

## 待辦（如果之後要動程式碼）

1. 在有 Rust 工具鏈的環境跑一次真實轉換，產出 canvas.json，用 `verification_data/extract_nodes.py` 的方法做 20 節點抽樣結構比對，取得真正的「轉換成功率」而非靜態覆蓋率推估。
2. 視情況決定是否要把 Auto Layout 次軸欄位的改名邏輯補進 `field_alignment.rs`（成本低、效益高）。
3. Grid Layout / Component Properties 屬於新功能，需先確認官方資料在 Kiwi 內部對應的原始欄位名稱（目前完全沒有線索，需要對照 Figma 官方文檔或反向工程 schema）。
