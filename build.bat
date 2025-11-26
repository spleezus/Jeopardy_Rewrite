@echo off
REM Build script for Jeopardy Game executable (Windows)

echo ========================================
echo Jeopardy Game - Build Script
echo ========================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

echo Building executable...
echo.

REM Build the executable
pyinstaller --clean ^
    --onefile ^
    --name "JeopardyGame" ^
    --add-data "templates;templates" ^
    --add-data "game.csv;." ^
    --hidden-import=engineio.async_drivers.threading ^
    --hidden-import=socketio ^
    --hidden-import=flask ^
    --hidden-import=flask_socketio ^
    server.py

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: dist\JeopardyGame.exe
echo.
echo To run:
echo   1. Copy game.csv to the same folder as JeopardyGame.exe
echo   2. Double-click JeopardyGame.exe
echo.
pause
