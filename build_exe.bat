@echo off
title CleanClicks — Building EXE
color 0B
echo.
echo  ====================================================
echo   CleanClicks — Standalone EXE Builder v3.0
echo  ====================================================
echo.
echo  Building CleanClicks.exe — single file your friend
echo  just double-clicks. No Python. No install. Nothing.
echo.
echo  Build time: 2-4 minutes
echo.
pause

:: ── Verify correct folder ─────────────────────────────────────────────────────
if not exist "cleaner_backend.py" (
    echo.
    echo  [ERROR] Run this from your CleanClicks folder!
    echo  Expected: D:\Desktop cleaner\CleanClicks\
    echo.
    pause
    exit /b 1
)
if not exist "cleanclicks_launcher.py" (
    echo.
    echo  [ERROR] cleanclicks_launcher.py not found!
    echo  Download it from the latest update and try again.
    echo.
    pause
    exit /b 1
)

:: ── Step 1: Install dependencies ─────────────────────────────────────────────
echo.
echo  [1/4] Installing build tools...
pip install pyinstaller waitress --quiet
if %errorlevel% NEQ 0 (
    echo.
    echo  [ERROR] pip install failed!
    echo  Try running as Administrator.
    echo.
    pause
    exit /b 1
)
echo  Done.

:: ── Step 2: Generate icon ─────────────────────────────────────────────────────
echo.
echo  [2/4] Creating app icon...
pip install pillow --quiet >nul 2>&1
python create_icon.py
if exist "cleanclicks.ico" (
    echo  Icon created.
    set ICON=--icon cleanclicks.ico
) else (
    echo  Icon skipped - using default.
    set ICON=
)

:: ── Step 3: Clean previous build ──────────────────────────────────────────────
echo.
echo  [3/4] Cleaning old build...
if exist "dist\CleanClicks.exe" del /f /q "dist\CleanClicks.exe" >nul 2>&1
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "CleanClicks.spec" del /f /q "CleanClicks.spec" >nul 2>&1
echo  Clean.

:: ── Step 4: Build EXE ─────────────────────────────────────────────────────────
echo.
echo  [4/4] Building CleanClicks.exe...
echo  Please wait 2-4 minutes - do NOT close this window!
echo.

pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "CleanClicks" ^
    %ICON% ^
    --add-data "cleanclicks.html;." ^
    --add-data "cleaner_backend.py;." ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --hidden-import=waitress ^
    --hidden-import=winreg ^
    --hidden-import=threading ^
    --hidden-import=webbrowser ^
    cleanclicks_launcher.py

echo.
echo  ====================================================
echo   Build process finished. Checking result...
echo  ====================================================
echo.

:: ── Check result ──────────────────────────────────────────────────────────────
if not exist "dist\CleanClicks.exe" (
    echo.
    echo  ====================================================
    echo   BUILD FAILED - EXE was not created.
    echo.
    echo   Scroll up and look for lines with ERROR or WARNING
    echo   Take a screenshot and share it.
    echo.
    echo   Common fixes:
    echo   1. Run as Administrator
    echo   2. Disable antivirus temporarily during build
    echo   3. Run this command manually:
    echo      pip install --upgrade pyinstaller
    echo  ====================================================
    echo.
    pause
    exit /b 1
)

:: ── Copy HTML next to EXE ─────────────────────────────────────────────────────
copy /y "cleanclicks.html" "dist\cleanclicks.html" >nul

:: ── Create README ─────────────────────────────────────────────────────────────
(
echo CleanClicks v3.0
echo ================
echo.
echo HOW TO USE:
echo 1. Keep CleanClicks.exe and cleanclicks.html in the SAME folder
echo 2. Double-click CleanClicks.exe
echo 3. Your browser opens automatically - app is ready!
echo.
echo If Windows shows a warning:
echo   Click "More info" then "Run anyway"
echo   CleanClicks is free and safe - no malware.
echo.
echo TO CLOSE: close your browser or end CleanClicks in Task Manager.
) > "dist\README.txt"

:: ── Show file size ────────────────────────────────────────────────────────────
for %%A in ("dist\CleanClicks.exe") do set SIZE=%%~zA
set /a MB=%SIZE% / 1048576

echo.
echo  ====================================================
echo   SUCCESS! CleanClicks.exe is ready!
echo.
echo   Location : D:\Desktop cleaner\CleanClicks\dist\
echo   File size: %MB% MB
echo.
echo   Send your friend BOTH files:
echo     CleanClicks.exe
echo     cleanclicks.html
echo.
echo   They just double-click CleanClicks.exe
echo   Browser opens. App is ready. Done.
echo  ====================================================
echo.

explorer dist
pause
