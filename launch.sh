#!/bin/bash
# Jeopardy Game Launcher for Mac/Linux

echo "========================================"
echo "      JEOPARDY GAME LAUNCHER"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null
then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    echo "Or use your package manager:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

echo "[OK] Python is installed"
python3 --version
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "ERROR: pip3 is not installed!"
    echo "Please install pip3:"
    echo "  macOS: python3 -m ensurepip --upgrade"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  Fedora: sudo dnf install python3-pip"
    exit 1
fi

echo "[OK] pip is installed"
echo ""

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo "ERROR: requirements.txt not found!"
    echo "Please make sure requirements.txt is in the same folder as this script"
    exit 1
fi

echo "Checking and installing required packages..."
echo ""

# Install/upgrade requirements
pip3 install -r requirements.txt --quiet --user
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Some packages may have failed to install"
    echo "Trying without --quiet flag to see details..."
    echo ""
    pip3 install -r requirements.txt --user
fi

echo ""
echo "========================================"
echo "  ALL REQUIREMENTS INSTALLED!"
echo "========================================"
echo ""

# Check if game.csv exists
if [ ! -f game.csv ]; then
    echo "WARNING: game.csv not found!"
    echo "The game will start but you'll need to create game.csv"
    echo ""
fi

echo "Starting Jeopardy Game Server..."
echo ""
echo "The TV display will automatically open in your browser"
echo ""
echo "To access other pages:"
echo "  - Host Panel: Visit http://localhost:5000/host"
echo "  - Player Join: Visit http://localhost:5000/player"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================"
echo ""

# Run the game server
python3 server.py

# If server exits, pause so user can see any errors
echo ""
echo "Server stopped. Press Enter to exit..."
read
