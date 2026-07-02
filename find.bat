@echo off
REM Search translate.csv:  find.bat Bekapcsol   |   find.bat "Turn On"
where python >nul 2>nul || (echo Python 3 is required but was not found on PATH. & pause & exit /b 1)
python "%~dp0scripts\find.py" %*
echo.
pause
