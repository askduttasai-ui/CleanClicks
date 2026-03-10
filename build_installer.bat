@echo off
title CleanClicks — Building Setup Installer
color 0B
echo.
echo  ====================================================
echo   CleanClicks — Professional Installer Builder
echo  ====================================================
echo.
echo  Builds CleanClicks_Setup.exe
echo  User experience: Next, Next, Install, Finish
echo  Desktop shortcut created automatically.
echo.
pause

:: ── Verify correct folder ─────────────────────────────────────────────────────
if not exist "cleaner_backend.py" (
    echo [ERROR] Run from your CleanClicks folder!
    pause & exit /b 1
)
if not exist "dist\CleanClicks.exe" (
    echo.
    echo [ERROR] dist\CleanClicks.exe not found!
    echo Run build_exe.bat first, then run this script.
    pause & exit /b 1
)

:: ── Step 1: Check NSIS ────────────────────────────────────────────────────────
echo.
echo [1/4] Checking for NSIS...

set MAKENSIS=
if exist "C:\Program Files (x86)\NSIS\makensis.exe" set MAKENSIS=C:\Program Files (x86)\NSIS\makensis.exe
if exist "C:\Program Files\NSIS\makensis.exe" set MAKENSIS=C:\Program Files\NSIS\makensis.exe

if defined MAKENSIS (
    echo  NSIS found.
    goto :icon
)

:: NSIS not found - ask user to install manually
echo.
echo  NSIS is required to build the installer.
echo  It is free and takes 1 minute to install.
echo.
echo  Opening NSIS download page now...
echo  1. Download nsis-3.xx-setup.exe
echo  2. Run it and click Next, Next, Install
echo  3. Come back and run this script again
echo.
start https://nsis.sourceforge.io/Download
pause
exit /b 1

:icon
:: ── Step 2: Icon and banner ───────────────────────────────────────────────────
echo.
echo [2/4] Creating graphics...
if not exist "cleanclicks.ico" python create_icon.py
python create_banner.py
echo  Done.

:: ── Step 3: Clean old installer ──────────────────────────────────────────────
echo.
echo [3/4] Cleaning old build...
if exist "CleanClicks_Setup.exe" del /f /q "CleanClicks_Setup.exe"
echo  Clean.

:: ── Step 4: Build installer ───────────────────────────────────────────────────
echo.
echo [4/4] Building CleanClicks_Setup.exe...
echo.

"%MAKENSIS%" CleanClicks_Installer.nsi

:: ── Verify ────────────────────────────────────────────────────────────────────
echo.
if not exist "CleanClicks_Setup.exe" (
    echo  ====================================================
    echo   BUILD FAILED - Check errors above.
    echo  ====================================================
    pause & exit /b 1
)

for %%A in ("CleanClicks_Setup.exe") do set SIZE=%%~zA
set /a MB=%SIZE% / 1048576

echo.
echo  ====================================================
echo   SUCCESS! CleanClicks_Setup.exe is ready!
echo.
echo   Size: %MB% MB
echo.
echo   Send this ONE file to your friend:
echo   CleanClicks_Setup.exe
echo.
echo   They just double-click and follow:
echo   Next - I Agree - Install - Finish
echo   Desktop shortcut created automatically!
echo  ====================================================
echo.
explorer .
pause
