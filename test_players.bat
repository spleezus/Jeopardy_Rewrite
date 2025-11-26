@echo off
REM Quick launcher for player simulator

echo ========================================
echo   JEOPARDY - PLAYER SIMULATOR
echo ========================================
echo.
echo This will simulate 30 players joining
echo and buzzing in automatically.
echo.
echo Make sure the game server is running!
echo (Run launch.bat first)
echo.
pause

python test_players.py

pause
