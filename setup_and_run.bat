@echo off
cd /d "%~dp0"

echo ========================================
echo League of Legends Champion Rune Builder
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found!
echo.

echo Checking/Installing requirements...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo WARNING: Failed to install some requirements
    echo The application might not work properly
    echo.
)

echo.
echo Starting Rune Builder...
python champion_rune_builder.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo Please check the error messages above
)

pause