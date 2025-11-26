#!/bin/bash
# Fix missing websocket-client package

echo "========================================"
echo "  FIXING WEBSOCKET-CLIENT PACKAGE"
echo "========================================"
echo ""
echo "Installing websocket-client..."
echo ""

pip3 install websocket-client --user

echo ""
echo "========================================"
echo "  DONE!"
echo "========================================"
echo ""
echo "Now try running ./test_players.sh again"
echo ""
