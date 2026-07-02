@echo off
REM Extract the current English Game.locres from the game's pak and refresh translate.csv
where python >nul 2>nul || (echo Python 3 is required but was not found on PATH. Install it from python.org and tick "Add to PATH". & pause & exit /b 1)
python "%~dp0scripts\getlocres.py"
echo.
pause
