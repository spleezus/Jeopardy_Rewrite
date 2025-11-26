@echo off
REM Fix missing websocket-client package

echo ========================================
echo   FIXING WEBSOCKET-CLIENT PACKAGE
echo ========================================
echo.
echo Installing websocket-client...
echo.

pip install websocket-client

echo.
echo ========================================
echo   DONE!
echo ========================================
echo.
echo Now try running test_players.bat again
echo.
pause
