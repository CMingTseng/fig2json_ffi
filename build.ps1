# fig2json_ffi build script for Windows

$ErrorActionPreference = "Stop"

Write-Host "Starting fig2json_ffi build for Windows..." -ForegroundColor Cyan

# 1. Desktop (Windows x86_64)
Write-Host "Building Windows Desktop library..."
cargo build --release

# 2. Android (Requires Android NDK and targets installed)
# rustup target add aarch64-linux-android x86_64-linux-android
if (Get-Command "cargo-ndk" -ErrorAction SilentlyContinue) {
    Write-Host "Building Android targets..."
    cargo ndk -t arm64-v8a -t x86_64 build --release
} else {
    Write-Host "Skipping Android build: 'cargo-ndk' not installed. Install with 'cargo install cargo-ndk'." -ForegroundColor Yellow
}

Write-Host "Build complete! Artifacts can be found in the 'target\' directory." -ForegroundColor Green
