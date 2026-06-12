# Fig2Json 自動化流程架構圖

本文件說明從原始 Figma 設計稿到最終 UI 程式碼的完整自動化路徑。

## 流程概覽

```mermaid
graph TD
    A[Figma Design File .fig] -->|CLI Tool| B(fig2json Parser)
    
    subgraph "fig2json Core (Rust)"
        B --> C[Kiwi Binary Decoding]
        C --> D[Tree Construction]
        D --> E{62 Transformation Rules}
        E -->|Cleanup & Optimization| F[LLM-Friendly JSON]
    end
    
    F -->|Input| G[LLM / AI Model]
    
    subgraph "AI Generation Phase"
        G --> H[Code Generation Prompt]
        H --> I{Implementation}
        I -->|HTML/CSS| J[Web UI]
        I -->|Kotlin/Compose| K[Android UI]
    }
    
    style B fill:#f96,stroke:#333,stroke-width:2px
    style F fill:#00c,stroke:#fff,stroke-width:2px,color:#fff
    style G fill:#0c0,stroke:#333,stroke-width:2px
```

## 關鍵階段說明

1.  **Figma 源文件**: 使用者從 Figma 導出的本地 `.fig` 檔案。
2.  **fig2json Core**:
    *   **二進制解碼**: 處理複雜的 Kiwi 格式。
    *   **轉換規則**: 這是本專案的核心競爭力，透過 62 項規則（如坐標轉換、顏色簡化、冗餘移除）將「機器語言」轉化為「設計語義」。
3.  **LLM-Friendly JSON**: 產出的 JSON 檔案體積小、結構清晰，能讓 AI 在有限的 Context Window 內讀取更多有效資訊。
4.  **AI 生成階段**: 開發者透過特定的 Prompt 指南，讓 AI 扮演工程師角色，實現設計到程式碼的自動轉換。
