@echo off
title CleanClicks Installer
color 0B
echo.
echo  ====================================================
echo   CleanClicks -- PC Cleaner Installer
echo  ====================================================
echo.

:: Check for admin
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo  [ERROR] Please right-click install.bat and choose
    echo          "Run as administrator"
    pause
    exit /b 1
)

:: -- Step 1: Check Python ----------------------------------------
echo  [1/5] Checking for Python...
python --version >nul 2>&1
if %errorlevel% NEQ 0 (
    echo  Python not found. Downloading...
    curl -L -o "%TEMP%\python_installer.exe" https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del "%TEMP%\python_installer.exe"
    call refreshenv >nul 2>&1
)
echo  [OK] Python found.

:: -- Step 2: Install packages ------------------------------------
echo  [2/5] Installing required packages...
pip install flask flask-cors pywin32 packaging --quiet --break-system-packages 2>nul || pip install flask flask-cors pywin32 packaging --quiet
echo  [OK] Packages installed.

:: -- Step 3: Install Windows Service -----------------------------
echo  [3/5] Registering CleanClicks as a Windows Service...
sc stop CleanClicksService >nul 2>&1
sc delete CleanClicksService >nul 2>&1
timeout /t 2 /nobreak >nul
python cleanclicks_service.py install >nul 2>&1
sc config CleanClicksService start= auto >nul 2>&1
sc failure CleanClicksService reset= 86400 actions= restart/5000/restart/10000/restart/30000 >nul 2>&1
python cleanclicks_service.py start >nul 2>&1
echo  [OK] Service installed and started.

:: -- Step 4: Desktop Shortcut (opens localhost:4242) -------------
echo  [4/5] Creating Desktop shortcut...
set SHORTCUT=%USERPROFILE%\Desktop\CleanClicks.lnk
powershell -WindowStyle Hidden -Command "$ws=New-Object -ComObject WScript.Shell; $sc=$ws.CreateShortcut('%SHORTCUT%'); $sc.TargetPath='C:\Windows\explorer.exe'; $sc.Arguments='http://localhost:4242'; $sc.Description='CleanClicks PC Cleaner'; $sc.Save()"
echo  [OK] Desktop shortcut created.

:: -- Step 5: Launch ----------------------------------------------
echo  [5/5] Launching CleanClicks...
timeout /t 3 /nobreak >nul
start "" http://localhost:4242

echo.
echo  ====================================================
echo   CleanClicks is ready!
echo   Open anytime: http://localhost:4242
echo   Desktop shortcut also created!
echo  ====================================================
echo.
pause
