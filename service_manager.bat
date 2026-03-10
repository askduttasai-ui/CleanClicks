@echo off
title CleanClicks Service Manager
color 0B
:menu
cls
echo.
echo  ====================================================
echo   🧹  CleanClicks — Service Manager
echo  ====================================================
echo.
echo   1. Start  Service
echo   2. Stop   Service
echo   3. Restart Service
echo   4. Check  Status
echo   5. Exit
echo.
set /p choice= Enter option (1-5): 

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" exit

:start
net start CleanClicksService
pause & goto menu

:stop
net stop CleanClicksService
pause & goto menu

:restart
net stop CleanClicksService
timeout /t 2 /nobreak >nul
net start CleanClicksService
pause & goto menu

:status
sc query CleanClicksService
pause & goto menu
