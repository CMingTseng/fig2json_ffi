# Figma to JSON Conversion Optimization Report

## Overview
This document records the analysis of output file size inflation and the optimizations implemented in the `fig2json` tool to ensure the generated JSON remains efficient and focused on rendering data.

## 1. Problem: Large File Size
The initial output in `json_phase1_complete/canvas.json` was approximately **434MB**, significantly larger than the previous version (~138MB).

### Root Causes Identified:
*   **Unrefined Component Metadata**: The `components` map contained entire node structures for every symbol, including internal Figma data, geometry, and edit history.
*   **Disabled Cleanup Transformations**: Most data-stripping functions in `lib.rs` were commented out, leaving fields like `phase`, `editInfo`, `fillGeometry`, and `pluginData` in the output.
*   **Pretty Printing Overhead**: Standard indented JSON formatting increases file size by roughly 4x compared to compact representation.

## 2. Implementation & Fixes
The following changes were applied to the `fig2json` source code:

### Source Code Changes (`lib.rs`)
1.  **Enabled Logic**: Un-commented essential transformation passes:
    *   `transform_matrix_to_css`: Converts raw matrices to readable transform objects.
    *   `transform_colors_to_css`: Simplifies color representation.
    *   `remove_geometry_fields`: Strips internal path command data.
    *   `remove_phase_fields`: Removes Figma's internal lifecycle state.
    *   `remove_edit_info_fields`: Strips versioning and user edit metadata.
    *   `remove_image_metadata_fields`: Removes thumbnails and internal image flags.
2.  **Metadata Refinement**: Updated `extract_components_and_styles` to use `refine_metadata`, ensuring only keys like `name`, `description`, and `key` are preserved in the components map.

### Results
*   **Optimized Output Size**: **96MB** (Indented) / **22MB** (Compact).
*   **Quality**: High-fidelity design data without Figma's internal noise.

## 3. Comparison Commands
Use these commands to reproduce results or verify sizes:

```bash
# Generate optimized indented JSON (default)
cd fig2json && cargo run -- [input.fig] [output_dir]

# Generate compact JSON (smallest size)
cd fig2json && cargo run -- [input.fig] [output_dir] --compact

# Compare file sizes
ls -lh docs/SpayCardholder20260609.json json_phase1_complete/canvas.json
```

## 4. REST API Alignment & Further Improvements
To ensure the output is more compatible with the Figma REST API and even more efficient, the following adjustments were implemented:

### Structural Adjustments:
*   **Vector Data Removal**: Stripped the large `vectorData` object (internal Figma rendering data) which saved ~30% of file size.
*   **Field Renaming**:
    *   `fillPaints` → `fills`
    *   `strokePaints` → `strokes`
    *   (Matches Figma REST API naming conventions).
*   **Redundancy Cleanup**:
    *   Removed `size` field (already covered by `absoluteBoundingBox`).
    *   Removed `isPageDivider` (internal UI state).
    *   Stripped `dashPattern` when it is default `[0,0]`.

### Final Metrics:
*   **Initial Problematic Size**: 434MB
*   **Optimization Phase 1**: 96MB (Enabled basic cleanup)
*   **Optimization Phase 2**: **67MB** (Removed `vectorData` & Redundant fields)
*   **Compact Mode**: **15MB** (approx.)

## 5. Implementation Summary
The conversion logic in `lib.rs` now follows a stricter "REST-like" structure, discarding internal Figma engine properties that are unnecessary for JSON-to-Code or Web rendering workflows.
