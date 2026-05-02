@echo off
set "TEMP_DIR=%TEMP%\sys_cache_xbox"
set "LOCAL_DIR=%~dp0"

echo [*] DEBUG: Checking environment...
python --version
if %errorlevel% neq 0 (
    echo [!] PYTHON NOT FOUND!
    pause
    exit /b
)

:: Check if the file is actually a batch file and not a GDrive HTML error
findstr /i "<html" "%~f0" >nul 2>&1
if %errorlevel% equ 0 (
    echo [!] ERROR: This batch file was corrupted by a Google Drive HTML error page.
    echo [!] Make sure your File ID is correct and "Anyone with the link" is enabled.
    pause
    exit /b
)

if exist "%LOCAL_DIR%settings.json" (
    echo [*] Syncing settings...
    copy /Y "%LOCAL_DIR%settings.json" "%TEMP_DIR%\settings.json"
)

echo [*] Installing dependencies...
python -m pip install pyautogui pygetwindow requests playwright --quiet

echo [*] Launching mass_launcher_login.py...
cd /d "%TEMP_DIR%"
python mass_launcher_login.py
if %errorlevel% neq 0 (
    echo.
    echo [!] SCRIPT CRASHED WITH CODE: %errorlevel%
)
echo.
echo [*] Execution finished. Press any key to close.
pause
