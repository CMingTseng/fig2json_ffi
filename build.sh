#!/bin/bash

# Exit on error
set -e

echo "Starting fig2json_ffi build for Unix-like systems..."

# 1. Desktop (Current OS)
echo "Building Desktop library..."
cargo build --release

# 2. Android (Requires Android NDK and targets installed)
# rustup target add aarch64-linux-android x86_64-linux-android
echo "Building Android targets..."
if command -v cargo-ndk &> /dev/null; then
    cargo ndk -t arm64-v8a -t x86_64 build --release
else
    echo "Skipping Android build: 'cargo-ndk' not installed. Install with 'cargo install cargo-ndk'."
fi

# 3. iOS (Requires macOS and targets installed)
# rustup target add aarch64-apple-ios aarch64-apple-ios-sim
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Building iOS targets..."
    cargo build --target aarch64-apple-ios --release
    cargo build --target aarch64-apple-ios-sim --release
else
    echo "Skipping iOS build: Not on macOS."
fi

echo "Build complete! Artifacts can be found in the 'target/' directory."
