@echo off
cls
echo ========================================
echo    LAN File Collector - Start Server
echo ========================================
echo.
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python not found in PATH!
    echo Please install Python 3 from:
    echo https://www.python.org/downloads/windows/
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo Found: %%i
echo Python OK.
echo.

echo [2/3] Checking dependencies...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Flask not found, installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Please check your internet connection.
        echo.
        pause
        exit /b 1
    )
)
echo Dependencies OK.
echo.

echo [3/3] Set save directory
echo.
echo Default save folder: D:\uploads
echo.
set /p SAVE_PATH=Enter save path (press Enter for default): 

if "%SAVE_PATH%"=="" (
    echo.
    echo Starting server with default path...
    python server.py
) else (
    echo.
    echo Starting server with custom path: %SAVE_PATH%
    python server.py "%SAVE_PATH%"
)

pause
