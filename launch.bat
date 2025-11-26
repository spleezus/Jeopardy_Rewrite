@echo off
REM Jeopardy Game Launcher
REM Checks requirements, installs if needed, launches game

echo ========================================
echo       JEOPARDY GAME LAUNCHER
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed!
    echo Please reinstall Python with pip included
    pause
    exit /b 1
)

echo [OK] pip is installed
echo.

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo ERROR: requirements.txt not found!
    echo Please make sure requirements.txt is in the same folder as this script
    pause
    exit /b 1
)

echo Checking and installing required packages...
echo.

REM Install/upgrade requirements
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo WARNING: Some packages may have failed to install
    echo Trying without --quiet flag to see details...
    echo.
    pip install -r requirements.txt
)

echo.
echo ========================================
echo   ALL REQUIREMENTS INSTALLED!
echo ========================================
echo.

REM Check if game.csv exists
if not exist game.csv (
    echo WARNING: game.csv not found!
    echo The game will start but you'll need to create game.csv
    echo.
)

echo Starting Jeopardy Game Server...
echo.
echo The TV display will automatically open in your browser
echo.
echo To access other pages:
echo   - Host Panel: Press 'H' or visit /host
echo   - Player Join: Press 'P' or visit /player
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Run the game server
python server.py

REM If server exits, pause so user can see any errors
pause
