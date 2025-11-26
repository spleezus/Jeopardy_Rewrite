#!/bin/bash
# Build script for Jeopardy Game executable

echo "========================================"
echo "Jeopardy Game - Build Script"
echo "========================================"
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

echo "Building executable..."
echo ""

# Build the executable
pyinstaller --clean \
    --onefile \
    --name "JeopardyGame" \
    --add-data "templates:templates" \
    --add-data "game.csv:." \
    --hidden-import=engineio.async_drivers.threading \
    --hidden-import=socketio \
    --hidden-import=flask \
    --hidden-import=flask_socketio \
    server.py

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Executable location: dist/JeopardyGame"
echo ""
echo "To run:"
echo "  1. Copy game.csv to the same folder as JeopardyGame"
echo "  2. Run ./JeopardyGame (Mac/Linux) or JeopardyGame.exe (Windows)"
echo ""
