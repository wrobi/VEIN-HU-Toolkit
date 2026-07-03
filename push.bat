@echo off
REM Commit + sync + push the toolkit to GitHub with clean, linear history.
REM add -A -> commit -> pull --rebase -> push  (no merge/amend divergence traps)
setlocal EnableDelayedExpansion
cd /d "%~dp0"

where git >nul 2>nul || (echo Git is required but was not found on PATH. & pause & exit /b 1)

echo Staging all changes...
git add -A

git diff --cached --quiet
if errorlevel 1 goto commit
echo Nothing new to commit.
goto sync

:commit
set "msg="
set /p "msg=Commit message [translating]: "
if "!msg!"=="" set "msg=translating"
git commit -m "!msg!"
if errorlevel 1 (echo Commit failed. & pause & exit /b 1)

:sync
echo.
echo Syncing with GitHub (rebase)...
git pull --rebase
if errorlevel 1 goto conflict

echo.
echo Pushing...
git push
if errorlevel 1 (echo Push failed. & pause & exit /b 1)

echo.
echo Done - GitHub is up to date.
pause
exit /b 0

:conflict
echo.
echo *** Rebase hit a conflict - aborting to stay safe. ***
git rebase --abort
echo Nothing was pushed. Ask Claude to help reconcile.
pause
exit /b 1
