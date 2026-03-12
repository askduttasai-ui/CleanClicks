@echo off
title CleanClicks — Building EXE
color 0B
echo.
echo  ====================================================
echo   CleanClicks — Standalone EXE Builder v3.3
echo  ====================================================
echo.
echo  Building CleanClicks.exe using Python 3.11
echo  No Python needed for end users. Just double-click!
echo.
echo  Build time: 2-4 minutes
echo.
pause

:: ── Verify correct folder ─────────────────────────────────────────────────────
if not exist "cleaner_backend.py" (
    echo.
    echo  [ERROR] Run this from your CleanClicks folder!
    echo.
    pause
    exit /b 1
)
if not exist "cleanclicks_launcher.py" (
    echo.
    echo  [ERROR] cleanclicks_launcher.py not found!
    echo.
    pause
    exit /b 1
)
if not exist "cleanclicks.html" (
    echo.
    echo  [ERROR] cleanclicks.html not found!
    echo.
    pause
    exit /b 1
)

:: ── Auto-detect Python 3.11 ───────────────────────────────────────────────────
echo  Detecting Python 3.11...

:: Try PATH first (most common)
set PYTHON311=
for /f "delims=" %%i in ('where python 2^>nul') do (
    if not defined PYTHON311 (
        "%%i" --version 2>&1 | find "3.11" >nul && set PYTHON311=%%i
    )
)

:: Try common install locations if not found in PATH
if not defined PYTHON311 (
    for %%u in ("%USERPROFILE%", "C:\Users\%USERNAME%") do (
        for %%p in (
            "%%~u\AppData\Local\Programs\Python\Python311\python.exe"
            "%%~u\AppData\Local\Programs\Python\Python311-32\python.exe"
        ) do (
            if not defined PYTHON311 (
                if exist %%p set PYTHON311=%%p
            )
        )
    )
)

:: Try system-wide install
if not defined PYTHON311 (
    for %%p in (
        "C:\Python311\python.exe"
        "C:\Program Files\Python311\python.exe"
        "C:\Program Files (x86)\Python311\python.exe"
    ) do (
        if not defined PYTHON311 (
            if exist %%p set PYTHON311=%%p
        )
    )
)

if not defined PYTHON311 (
    echo.
    echo  [ERROR] Python 3.11 not found!
    echo  Please install Python 3.11 from https://python.org
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo  Found: %PYTHON311%

:: Derive pip and pyinstaller paths from python path
for %%i in ("%PYTHON311%") do set PYDIR=%%~dpi
set PIP311=%PYDIR%Scripts\pip.exe
set PYINSTALLER311=%PYDIR%Scripts\pyinstaller.exe

:: ── Step 1: Install dependencies ─────────────────────────────────────────────
echo.
echo  [1/4] Installing build tools...
"%PIP311%" install pyinstaller pywin32 flask flask-cors waitress pillow psutil --quiet
if %errorlevel% NEQ 0 (
    echo.
    echo  [ERROR] pip install failed! Try running as Administrator.
    pause
    exit /b 1
)
echo  Done.

:: ── Step 2: Generate icon ─────────────────────────────────────────────────────
echo.
echo  [2/4] Creating app icon...
"%PYTHON311%" create_icon.py
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

"%PYINSTALLER311%" ^
    --onefile ^
    --noconsole ^
    --name "CleanClicks" ^
    %ICON% ^
    --add-data "cleanclicks.html;." ^
    --add-data "cleaner_backend.py;." ^
    --add-data "cleanclicks_service.py;." ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --hidden-import=waitress ^
    --hidden-import=winreg ^
    --hidden-import=threading ^
    --hidden-import=webbrowser ^
    --hidden-import=psutil ^
    --hidden-import=win32serviceutil ^
    --hidden-import=win32service ^
    --hidden-import=win32event ^
    --hidden-import=servicemanager ^
    --hidden-import=win32api ^
    --hidden-import=win32con ^
    --hidden-import=pywintypes ^
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
    echo   Common fixes:
    echo   1. Run as Administrator
    echo   2. Disable antivirus temporarily during build
    echo   3. Run: pip install --upgrade pyinstaller
    echo  ====================================================
    echo.
    pause
    exit /b 1
)

:: ── Copy files next to EXE ────────────────────────────────────────────────────
copy /y "cleanclicks.html"       "dist\cleanclicks.html"       >nul
copy /y "cleanclicks_service.py" "dist\cleanclicks_service.py" >nul
if exist "cleanclicks.ico" copy /y "cleanclicks.ico" "dist\cleanclicks.ico" >nul

:: ── Create README ─────────────────────────────────────────────────────────────
(
echo CleanClicks v3.3
echo ================
echo.
echo HOW TO USE:
echo 1. Double-click CleanClicks.exe
echo 2. Your browser opens automatically at http://localhost:5050
echo 3. App is ready!
echo.
echo If Windows shows a warning:
echo   Click "More info" then "Run anyway"
echo   CleanClicks is free and safe - no malware.
echo.
echo SOURCE: https://github.com/askduttasai-ui/CleanClicks
) > "dist\README.txt"

:: ── Show file size ────────────────────────────────────────────────────────────
for %%A in ("dist\CleanClicks.exe") do set SIZE=%%~zA
set /a MB=%SIZE% / 1048576

echo.
echo  ====================================================
echo   SUCCESS! CleanClicks.exe is ready!
echo.
echo   Location : dist\CleanClicks.exe
echo   File size: %MB% MB
echo  ====================================================
echo.

explorer dist
pause
