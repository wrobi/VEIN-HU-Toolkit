@echo off
REM Build VEIN_HUN.pak from translate.csv + Game.locres
where python >nul 2>nul || (echo Python 3 is required but was not found on PATH. Install it from python.org and tick "Add to PATH". & pause & exit /b 1)
python "%~dp0scripts\build.py"
echo.
pause
