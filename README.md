# fig2json_ffi

[English](#english) | [繁體中文](#繁體中文) | [简体中文](#简体中文)

---

## English

### Introduction
**fig2json_ffi** is a Foreign Function Interface (FFI) bridge for the [fig2json](https://github.com/kreako/fig2json) project. It provides a lightweight wrapper around the core Rust logic, making it accessible to **JVM**, **Android**, and **iOS (Native)** platforms.

### Why this project?
The primary goal of this repository is to provide platform-specific FFI bindings for `fig2json` without modifying the original Rust codebase.
1.  **Isolation**: The original `fig2json` remains focused solely on Rust logic and CLI features.
2.  **Clean Upstream**: JNI and C-Interop configurations are managed here as a separate layer, keeping the upstream repository clean.
3.  **Submodule Integration**: `fig2json` is integrated as a git submodule to ensure synchronization with the latest Rust core.

### Integration Guide

#### 1. Android
-   **Artifact**: `.so` files (e.g., `libfig2json.so`).
-   **Usage**: Place the compiled `.so` files in your Android project's `src/main/jniLibs/{arch}/` directory.
-   **Loading**: Use `System.loadLibrary("fig2json")` in Kotlin/Java.

#### 2. iOS (Kotlin Multiplatform / Native)
-   **Artifact**: `.a` (static library).
-   **Usage**: 
    1.  Add the `.a` file to your project.
    2.  Configure `cinterop` in your `build.gradle.kts` using the provided `fig2json.h` and `.def` file.
    3.  Link the library using `linkerOpts("-lfig2json")`.

#### 3. JVM (Desktop)
-   **Artifact**: `.dylib` (macOS), `.so` (Linux), or `.dll` (Windows).
-   **Usage**: Ensure the library is in your system path or bundled within your application resources.
-   **Loading**: Use `System.loadLibrary("fig2json")` or `System.load("/path/to/library")`.

---

## 繁體中文

### 簡介
**fig2json_ffi** 是 [fig2json](https://github.com/kreako/fig2json) 專案的外部函式介面 (FFI) 橋接層。它為 Rust 核心邏輯提供輕量級包裝，使其能在 **JVM**、**Android** 以及 **iOS (Native)** 平台被呼叫。

### 為什麼要有這個專案？
本專案的主要目的是在不修改原始 Rust 代碼的前提下，為 `fig2json` 提供各平台的 FFI 綁定：
1.  **職責分離**：原始的 `fig2json` 可以維持純粹的 Rust 邏輯與 CLI 工具開發。
2.  **保持上游整潔**：所有的 JNI 與 C-Interop 配置都集中在此橋接層，避免「污染」原始倉庫。
3.  **子模組集成**：透過 git submodule 引入 `fig2json`，確保與最新 Rust 核心同步。

### 整合指南

#### 1. Android
-   **產物**: `.so` 檔案 (例如 `libfig2json.so`)。
-   **用法**: 將編譯好的 `.so` 檔案放入 Android 專案的 `src/main/jniLibs/{arch}/` 目錄下。
-   **載入**: 在 Kotlin/Java 中使用 `System.loadLibrary("fig2json")`。

#### 2. iOS (Kotlin Multiplatform / Native)
-   **產物**: `.a` (靜態庫)。
-   **用法**:
    1.  將 `.a` 檔案加入專案。
    2.  在 `build.gradle.kts` 中使用提供的 `fig2json.h` 與 `.def` 檔案配置 `cinterop`。
    3.  使用 `linkerOpts("-lfig2json")` 進行連結。

#### 3. JVM (Desktop)
-   **產物**: `.dylib` (macOS), `.so` (Linux), 或 `.dll` (Windows)。
-   **用法**: 確保函式庫位於系統路徑中，或打包在應用程式資源內。
-   **載入**: 使用 `System.loadLibrary("fig2json")` 或 `System.load("/路徑/到/函式庫")`。

---

## 简体中文

### 简介
**fig2json_ffi** 是 [fig2json](https://github.com/kreako/fig2json) 项目的外部函数接口 (FFI) 桥接层。它为 Rust 核心逻辑提供轻量级包装，使其能在 **JVM**、**Android** 以及 **iOS (Native)** 平台被调用。

### 为什么要有这个项目？
本项目的主要目的是在不修改原始 Rust 代码的前提下，为 `fig2json` 提供各平台的 FFI 绑定：
1.  **职责分离**：原始的 `fig2json` 可以维持纯粹的 Rust 逻辑与 CLI 工具开发。
2.  **保持上游整洁**：所有的 JNI 与 C-Interop 配置都集中在此桥接层，避免“污染”原始仓库。
3.  **子模块集成**：通过 git submodule 引入 `fig2json`，确保与最新 Rust 核心同步。

### 集成指南

#### 1. Android
-   **产物**: `.so` 文件 (例如 `libfig2json.so`)。
-   **用法**: 将编译好的 `.so` 文件放入 Android 项目的 `src/main/jniLibs/{arch}/` 目录下。
-   **加载**: 在 Kotlin/Java 中使用 `System.loadLibrary("fig2json")` 。

#### 2. iOS (Kotlin Multiplatform / Native)
-   **产物**: `.a` (静态库)。
-   **用法**:
    1.  将 `.a` 文件加入项目。
    2.  在 `build.gradle.kts` 中使用提供的 `fig2json.h` 与 `.def` 文件配置 `cinterop`。
    3.  使用 `linkerOpts("-lfig2json")` 进行链接。

#### 3. JVM (Desktop)
-   **产物**: `.dylib` (macOS), `.so` (Linux), 或 `.dll` (Windows)。
-   **用法**: 确保库文件位于系统路径中，或打包在应用程序资源内。
-   **加载**: 使用 `System.loadLibrary("fig2json")` 或 `System.load("/路径/到/库文件")`。
