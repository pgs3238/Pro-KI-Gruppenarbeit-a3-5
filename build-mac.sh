#!/bin/bash
# ============================================
# FINLY Build Script for macOS
# ============================================

echo ""
echo "========================================"
echo "   FINLY - macOS Build"
echo "========================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed!"
    echo "Please install Node.js from https://nodejs.org"
    exit 1
fi

# Check if npm dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "[INFO] Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies!"
        exit 1
    fi
fi

echo "[INFO] Building FINLY for macOS..."
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "   Build successful!"
    echo "========================================"
    echo ""
    echo "Find your dmg at:"
    echo "   dist/FINLY-1.0.0.dmg"
    echo ""
else
    echo ""
    echo "[ERROR] Build failed!"
    exit 1
fi
