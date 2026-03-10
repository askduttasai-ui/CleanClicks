@echo off
title CleanClicks Uninstaller
color 0C
echo.
echo  ====================================================
echo   🧹  CleanClicks — Uninstaller
echo  ====================================================
echo.
net session >nul 2>&1
if %errorlevel% NEQ 0 (echo  Run as Administrator! & pause & exit /b 1)

echo  Stopping service...
net stop CleanClicksService >nul 2>&1
python cleanclicks_service.py remove >nul 2>&1

echo  Removing Desktop shortcut...
del "%USERPROFILE%\Desktop\CleanClicks.lnk" >nul 2>&1

echo.
echo  ✅  CleanClicks has been removed.
echo  (Your files in this folder are NOT deleted.)
echo.
pause
