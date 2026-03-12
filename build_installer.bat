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
    goto :makefiles
)

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

:makefiles
:: ── Step 2: Auto-create required files ───────────────────────────────────────
echo.
echo [2/4] Creating required files...

if not exist "LICENSE.txt" (
    (echo MIT License
     echo.
     echo Copyright ^(c^) 2025 AK CleanClicks
     echo.
     echo Permission is hereby granted, free of charge, to any person obtaining a copy
     echo of this software and associated documentation files, to deal in the Software
     echo without restriction, including without limitation the rights to use, copy,
     echo modify, merge, publish, distribute, sublicense, and/or sell copies of the
     echo Software, and to permit persons to whom the Software is furnished to do so.
     echo.
     echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
    ) > LICENSE.txt
    echo  LICENSE.txt created.
) else ( echo  LICENSE.txt found. )

if not exist "README.txt" (
    (echo CleanClicks v3.3 - Free PC Cleaner
     echo Publisher: AK CleanClicks
     echo Website: https://cleanclicks.netlify.app
     echo.
     echo Double-click CleanClicks.exe to launch.
     echo Browser opens at http://localhost:5050
    ) > README.txt
    echo  README.txt created.
) else ( echo  README.txt found. )

if not exist "cleanclicks.ico" (
    python create_icon.py
    if exist "cleanclicks.ico" ( echo  Icon created. ) else ( echo  [WARNING] No icon found - using default. )
) else ( echo  cleanclicks.ico found. )

if exist "create_banner.py" python create_banner.py
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
echo   Send this ONE file to your friends:
echo     CleanClicks_Setup.exe
echo.
echo   They just double-click and follow:
echo     Next - I Agree - Install - Finish
echo   "Launch CleanClicks now" checkbox will appear!
echo   Desktop shortcut created automatically!
echo  ====================================================
echo.
explorer .
pause
