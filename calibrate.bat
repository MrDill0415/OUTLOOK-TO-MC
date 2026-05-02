@echo off
echo ==================================================
echo           ENI'S PIXEL CALIBRATOR
echo ==================================================

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Error: Python not found.
    pause
    exit /b
)

:: Install PyAutoGUI if missing
python -m pip install pyautogui --quiet

:: Run
python get_coords.py

if %errorlevel% neq 0 (
    echo.
    echo [!] Calibrator crashed.
    pause
)
pause
