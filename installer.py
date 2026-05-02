import os
import sys
import urllib.request
import tempfile
import subprocess
import shutil

# =============================================================================
# CONFIGURATION - USE YOUR GITHUB RAW URL
# =============================================================================
# 1. Create a Public GitHub repo.
# 2. Upload all files.
# 3. Use the URL for the "Raw" content of your main branch.
# Example: https://raw.githubusercontent.com/USER/REPO/main/
# =============================================================================
BASE_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/"
# =============================================================================

RUN_TOOL_BAT = r"""@echo off
set "TEMP_DIR=%TEMP%\sys_cache_xbox"
set "LOCAL_DIR=%~dp0"
echo [*] Syncing local settings...
if exist "%LOCAL_DIR%settings.json" copy /Y "%LOCAL_DIR%settings.json" "%TEMP_DIR%\settings.json" >nul
echo [*] Verifying dependencies...
python -m pip install pyautogui pygetwindow requests playwright --quiet >nul 2>&1
echo [*] Launching Xbox Elite...
cd /d "%TEMP_DIR%"
python mass_launcher_login.py
if %errorlevel% neq 0 pause
"""

CALIBRATE_BAT = r"""@echo off
echo [*] Starting Calibrator...
python -m pip install pyautogui --quiet >nul 2>&1
python get_coords.py
pause
"""

def download_file(url, dest_path):
    try:
        dir_name = os.path.dirname(dest_path)
        if dir_name: os.makedirs(dir_name, exist_ok=True)
        
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request) as response, open(dest_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print(f"[!] Error downloading {url}: {e}")
        return False

def main():
    temp_name = "sys_cache_xbox"
    install_dir = os.path.join(tempfile.gettempdir(), temp_name)
    os.makedirs(install_dir, exist_ok=True)
    accounts_dir = os.path.join(install_dir, "accounts_data")
    os.makedirs(accounts_dir, exist_ok=True)

    print("[*] Initializing environment...")

    # 1. Write Batch Files (Local)
    with open("run_tool.bat", "w") as f: f.write(RUN_TOOL_BAT)
    with open("calibrate.bat", "w") as f: f.write(CALIBRATE_BAT)

    # 2. Download Public/Tool Files (Local)
    print("[*] Fetching public tools...")
    for f in ["public.env", "get_coords.py", "settings.json"]:
        download_file(BASE_URL + f, f)

    # 3. Download Hidden Core (Temp)
    print("[*] Fetching core logic...")
    download_file(BASE_URL + "private.env", os.path.join(install_dir, ".env"))
    
    hidden = ["auth_handler.py", "key.txt", "keyauth.py", "launcher_bot.py", 
              "mass_launcher_login.py", "ms_login_playwright.py", "ui_automation.py"]
    for f in hidden:
        print(f"[*] Fetching {f}...")
        download_file(BASE_URL + f, os.path.join(install_dir, f))
    
    # Download accounts.txt to its subfolder in temp
    download_file(BASE_URL + "accounts_data/accounts.txt", os.path.join(accounts_dir, "accounts.txt"))

    # Sync local settings
    local_settings = os.path.join(os.getcwd(), "settings.json")
    temp_settings = os.path.join(install_dir, "settings.json")
    if os.path.exists(local_settings) and os.path.abspath(local_settings) != os.path.abspath(temp_settings):
        try:
            shutil.copy(local_settings, temp_settings)
        except:
            pass

    print("[+] Setup complete. Launching...")
    os.chdir(install_dir)
    
    # Launch silently using system python
    subprocess.Popen(["python", "mass_launcher_login.py"], 
                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    
    print("\n[DONE] Installation finished.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
