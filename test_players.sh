#!/bin/bash
# Quick launcher for player simulator

echo "========================================"
echo "  JEOPARDY - PLAYER SIMULATOR"
echo "========================================"
echo ""
echo "This will simulate 30 players joining"
echo "and buzzing in automatically."
echo ""
echo "Make sure the game server is running!"
echo "(Run ./launch.sh first)"
echo ""
read -p "Press Enter to start..."

python3 test_players.py
