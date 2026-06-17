# fig2json 覆蓋率修復報告

> 目標：將 `.fig` 二進位轉換輸出對齊 Figma REST API JSON 格式，達到 100% 欄位覆蓋率。

---

## 整體架構說明

```
Figma App（設計工具）
    ├── REST API 導出 → WawelEmlYBJ5sCIOQwycSJ_from_figma.json   ← 標準答案（~58,000 nodes）
    └── .fig 下載    → canvas.fig（Kiwi 二進位，資訊較少）
                              ↓
                        fig2json（Rust）
                              ↓
                        canvas_output.json   ← 轉換結果
                              ↓
                   compare_conversion.py
                   隨機抽 20 node，比對欄位 key 是否存在
                              ↓
                          覆蓋率分數
```

**覆蓋率不是 100% 的根本原因**：Kiwi 格式只儲存非預設值，且部分欄位在 .fig 裡以不同名稱或結構存放，需要 fig2json source code 補齊轉換邏輯。

---

## 目前覆蓋率（2026-06-17）

| 測試範圍 | 覆蓋率 | 說明 |
|---------|--------|------|
| 20-node sample（seed=42） | **88.6%** | 15/20 節點 100%，2 個節點找不到 |
| 5000-node broader sample（seed=0） | **98.87%** | 廣泛驗證用 |

---

## 修改的檔案與思路

### 1. `src/schema/transformations/field_alignment.rs`

**主要欄位改名與重組邏輯。**

#### Auto Layout（排版系統）

Kiwi 用舊版 `stack*` 前綴儲存，REST API 已改名。

| Kiwi 欄位 | REST API 欄位 | 修法 |
|-----------|--------------|------|
| `stackMode` | `layoutMode` | 直接改名 |
| `stackSpacing` | `itemSpacing` | 直接改名 |
| `stackHorizontalPadding` | `paddingLeft` | 只對應左側（不是左右對稱） |
| `stackPaddingRight` | `paddingRight` | 獨立欄位 |
| `stackVerticalPadding` | `paddingTop` | 只對應上側（不是上下對稱） |
| `stackPaddingBottom` | `paddingBottom` | 獨立欄位 |
| `stackWrap` | `layoutWrap` | 改名，WRAP 時額外補 `counterAxisSpacing` 和 `counterAxisAlignContent=AUTO` |
| `stackCounterSpacing=null` | `counterAxisSpacing` | WRAP 模式下 null → 用 itemSpacing 值 |
| `stackPositioning=ABSOLUTE` | `layoutPositioning=ABSOLUTE` | 改名 |
| `minSize.x/y` | `minWidth/minHeight` | 展開結構 |

> **關鍵陷阱**：`stackVerticalPadding` 不等於 paddingTop+paddingBottom，只等於 paddingTop。之前錯誤地 duplicate 到兩邊，導致 98 個節點的 paddingBottom 值錯誤。

#### Bound Variables（Design Token）

```
填充色的 colorVar 在 stopsVar[N].colorVar（gradient），不在頂層。
之前只讀頂層，導致 gradient 節點的 boundVariables 完全缺漏。
```

修法：遍歷 `fillPaints[N].stopsVar[M].colorVar`，加入 `boundVariables.fills`。

#### Vector 節點

| 欄位 | 來源 | 修法 |
|------|------|------|
| `cornerRadius` | `vectorData.styleOverrideTable` 的最大值 | 遍歷取 max |
| `rectangleCornerRadii` | 四個角個別值 `[tl, tr, br, bl]` | 從 cornerRadii 陣列重組 |
| `strokeDashes` | `dashPattern` 陣列 | 改名 |
| `strokeMiterAngle` | `miterLimit` | 改名換算 |
| `individualStrokeWeights` | `borderTopWeight` 等四個欄位 | 合併成物件 |
| `children: []` | 容器型 node 無子節點時 | 補空陣列 |

---

### 2. `src/schema/transformations/api_defaults.rs`（本次新增）

**補齊 Kiwi 省略的預設值，以及跨節點傳播邏輯。**

#### 全節點預設值注入

| 欄位 | 預設值 | 觸發條件 |
|------|--------|---------|
| `blendMode` | `"PASS_THROUGH"` | 所有節點（Kiwi 省略預設值） |
| `scrollBehavior` | `"SCROLLS"` | 無 scrollBehavior 時 |
| `scrollBehavior` | `"FIXED"` + `isFixed=true` | Kiwi 值為 `FIXED_WHEN_CHILD_OF_SCROLLING_FRAME` |
| `complexStrokeProperties` | `{"strokeType":"BASIC"}` | 所有節點 |
| `cornerSmoothing` | `0.0` | FRAME/RECTANGLE/VECTOR 等形狀節點 |
| `layoutWrap` | `"NO_WRAP"` | 有 layoutMode 的容器 |
| `backgroundColor` | `{r:0,g:0,b:0,a:0}` | FRAME/COMPONENT/INSTANCE/COMPONENT_SET |

#### Auto Layout 尺寸推算

```
layoutSizingHorizontal/Vertical：
  - HORIZONTAL layout 的 primary axis（水平）absent → HUG
  - HORIZONTAL layout 的 counter axis（垂直）absent → FIXED
  - VERTICAL 相反

primaryAxisSizingMode / counterAxisSizingMode：
  - 當對應 sizing 不是 HUG 時，補上 "FIXED"

子節點的 layoutGrow / layoutAlign：
  - layoutGrow absent → 0
  - layoutAlign absent → "INHERIT"

子節點的 layoutSizingH/V：
  - 根據 layoutGrow > 0 → FILL，否則 FIXED
  - 根據 layoutAlign == STRETCH → FILL，否則 FIXED
```

#### INSTANCE 對齊屬性傳播

**問題**：Kiwi 把 INSTANCE 的 layout override（`counterAxisAlignItems`、`primaryAxisAlignItems`）存在 INSTANCE 節點上，但 compound child frame 是從 COMPONENT template 複製出來的，不含這些 override。

**修法**：處理完 INSTANCE 節點後，找出 ID 含分號（compound）且有 `layoutMode` 的直屬子節點，用 `entry().or_insert()` 補入對應值。

---

### 3. `src/schema/transformations/relative_transform.rs`

**旋轉角度計算修正。**

原本只處理正常矩陣（`det > 0`），對於包含反射的矩陣（`det < 0`，例如水平翻轉的元件）旋轉角度算錯。

```
修前：rotation = atan2(m10, m11)   // 只適用 det > 0
修後：if det >= 0 → atan2(m10, m11)
      if det < 0  → atan2(m01, m00)  // 反射矩陣用另一組
```

---

### 4. `src/schema/transformations/type_alignment.rs`

**節點類型名稱對齊。**

Kiwi 的節點類型名稱在不同版本有不同的表示方式（string 或 enum object），統一處理：

```
SYMBOL → COMPONENT
ROUNDED_RECTANGLE → RECTANGLE
FRAME + isStateGroup=true → COMPONENT_SET
```

修前只處理 string 形式，修後同時處理 `{"__enum__": ..., "value": "TYPE_NAME"}` 的 enum object 形式。

---

## 尚未補齊的欄位

### 難度：高（架構限制，本次無法修復）

| 欄位 | 缺少節點數 | 根本原因 |
|------|-----------|---------|
| `fillOverrideTable` | ~292 (100%) | Kiwi 沒有這個結構，REST API 是伺服器從 vector network 重新計算的 |
| `componentPropertyReferences` | ~477 (100%) | 需要跨節點查 component property definition，目前無此查表邏輯 |
| `componentProperties` | ~385 (100%) | 同上，COMPONENT/COMPONENT_SET 節點的屬性定義系統 |
| `preserveRatio` | ~42 (100%) | Kiwi 無直接對應欄位（`targetAspectRatio` 僅 17.5% 可靠） |

### 難度：中（需要 instance override 傳播機制）

| 欄位 | 缺少節點數 | 根本原因 |
|------|-----------|---------|
| `cornerRadius`（compound nodes） | ~296 | INSTANCE override 不傳播到 compound child |
| `boundVariables`（compound nodes） | ~77 | 同上 |
| `primaryAxisAlignItems=SPACE_BETWEEN` | 4 | instance override + component variant 組合 |

**背景**：`tree.rs` 展開 INSTANCE 時，compound child 是從 COMPONENT template 複製的，INSTANCE 層的 override 欄位（cornerRadius、colorVar 等）沒有合併進去。要修需要在 `build_tree` 時實作 override 合併邏輯。

### 難度：中（觸發條件複雜）

| 欄位 | 缺少節點數 | 說明 |
|------|-----------|------|
| `rectangleCornerRadii=[0,0,0,0]` | ~1297 (72%) | VECTOR/GROUP 節點：沒有 vectorData 或全部 corner 為 0 時應補 `[0,0,0,0]`，但觸發條件與 cornerRadius 的互斥邏輯複雜 |

### 難度：低（尚未實作）

| 欄位 | 缺少節點數 | 說明 |
|------|-----------|------|
| `transitionNodeID` / `transitionDuration` / `transitionEasing` | 3–8 | Figma Prototype interaction，Kiwi 有儲存但目前未解析 |

---

## 20-node sample 卡關節點分析（seed=42）

| 節點 ID | 類型 | 覆蓋率 | 缺少欄位 | 可修性 |
|---------|------|--------|---------|--------|
| `I418:4337;230:4062;230:3921;230:3892;107:1496` | TEXT | 0%（找不到） | 全部 | 需調查 compound 展開深度 |
| `I17886:57032;418:3695;16840:8462` | VECTOR | 0%（找不到） | 全部 | 需調查 compound 展開深度 |
| `I16998:9438;130:4491` | VECTOR | 90% | `fillOverrideTable`, `rectangleCornerRadii` | 高難度 |
| `I17870:49472;17432:5889` | VECTOR | 85% | `fillOverrideTable`, `preserveRatio`, `rectangleCornerRadii` | 高難度 |
| `64:1115` | FRAME | 96.3% | `componentPropertyReferences` | 高難度 |

---

## 測試指令

```bash
# Build
cd fig2json
cargo build --release

# 轉換
cargo run --release -- ../fig_raw/canvas.fig -o ../canvas_output.json

# 跑覆蓋率測試
cd ..
python3 fig2json_ffi/docs/verification_data/compare_conversion.py \
  WawelEmlYBJ5sCIOQwycSJ_from_figma.json \
  canvas_output.json
```

---

## 理論上限評估

根據 Kiwi 格式的資訊量限制，即使完全修復所有可修欄位，理論最高覆蓋率約為 **~99.5%**，因為 `fillOverrideTable`、`preserveRatio`、`componentPropertyReferences` 等欄位的資料在 `.fig` 中根本不存在或無法還原。
