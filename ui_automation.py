import pyautogui
import pygetwindow as gw
import time
import os
import subprocess
import imaplib
import email
import re
import sys
import json

# =============================================================================
# DEFAULT CONFIGURATION (FALLBACK)
# =============================================================================
COORDS = {
    "step-1": (874, 584), "step-2": (845, 626), "step-4": (801, 628),
    "step-5": (949, 701), "step-7": (977, 546), "step-9": (776, 566),
    "step-11": (971, 710), "step-11b": (826, 452), "step-13": (971, 577),
    "step-14": (985, 770), "step-16": (832, 715), "step-17": (819, 534),
    "step-18": (964, 640), "step-19": (833, 789), "step-20": (1307, 675),
    "step-21": (842, 689)
}

DELAYS = {
    "init": 1, "step-1": 8, "step-2": 8, "step-3": 4, "step-4": 2, "step-5": 1,
    "step-6": 5, "step-7": 2, "step-8": 3, "step-9": 2, "step-10": 3,
    "step-11": 2, "step-11b": 2, "step-12": 15, "step-13": 5, "step-14": 5,
    "step-15": 2, "step-16": 15, "step-17": 8, "step-18": 2, "step-19": 3,
    "step-20": 30, "step-21": 5
}

PIN_CODE = "0415"
LAUNCHER_PATH = r"C:\XboxGames\Minecraft Launcher\Content\Minecraft.exe"

# =============================================================================
# SETTINGS LOADER
# =============================================================================
def apply_settings():
    global COORDS, DELAYS, PIN_CODE, LAUNCHER_PATH
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", "r") as f:
                data = json.load(f)
                if "COORDS" in data: COORDS = {k: tuple(v) for k, v in data["COORDS"].items()}
                if "DELAYS" in data: DELAYS = data["DELAYS"]
                if "PIN_CODE" in data: PIN_CODE = data["PIN_CODE"]
                if "LAUNCHER_PATH" in data: LAUNCHER_PATH = data["LAUNCHER_PATH"]
            print("\033[92m[+] Settings loaded from settings.json\033[0m")
        except Exception as e:
            print(f"\033[91m[!] Failed to load settings.json: {e}\033[0m")

apply_settings()

def load_env():
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
    return env_vars

def get_2fa_code(gmail_user, gmail_pass):
    print(f"[*] Checking 2FA for {gmail_user}...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_user, gmail_pass)
        mail.select("inbox")
        status, messages = mail.search(None, '(FROM "account-security-noreply@accountprotection.microsoft.com") UNSEEN')
        if status != "OK" or not messages[0]:
            status, messages = mail.search(None, '(FROM "microsoft.com") UNSEEN')
        if status != "OK" or not messages[0]:
            status, messages = mail.search(None, '(SUBJECT "security code") UNSEEN')
        if status != "OK" or not messages[0]:
            mail.logout()
            return None
        msg_id = messages[0].split()[-1]
        status, data = mail.fetch(msg_id, "(RFC822)")
        if status != "OK": 
            mail.logout()
            return None
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain" or content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode(errors='ignore')
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(errors='ignore')
        body = re.sub(r'<[^>]+>', ' ', body)
        code_match = re.search(r'\b\d{6,7}\b', body)
        mail.logout()
        if code_match:
            print(f"    [+] Found 2FA Code: {code_match.group(0)}")
            return code_match.group(0)
        return None
    except Exception as e:
        print(f"    [!] IMAP Error: {e}")
        return None

def countdown(step_key):
    n = DELAYS.get(step_key, 5)
    if n <= 0: return
    for i in range(n, 0, -1):
        sys.stdout.write(f"      \033[93m[\033[91m{i}s\033[93m]\033[0m   \r")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("      \033[92m[ACTION]\033[0m    \n")
    sys.stdout.flush()

def kill_launcher():
    processes = ["Minecraft.exe", "MinecraftLauncher.exe", "gamelaunchhelper.exe", "Minecraft.Windows.exe"]
    for proc in processes:
        subprocess.run(f'taskkill /F /IM "{proc}" /T', shell=True, capture_output=True)

def find_launcher():
    titles = ['Minecraft Launcher', 'Minecraft', 'Minecraft Launcher (Windows)']
    for _ in range(30):
        for title in titles:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                for w in windows:
                    if w.visible and w.title != "":
                        return w
        time.sleep(1)
    return None

def automate_login(email_addr, password):
    env = load_env()
    g2_user = env.get("GMAIL_USER_2", "N/A")
    g2_pass = env.get("GMAIL_PASS_2", "N/A")
    kill_launcher()
    print("\033[96m[*]\033[0m Task: \033[95mLauncher Init\033[0m")
    countdown("init")
    print(f"\033[96m[*]\033[0m Target: \033[92m{email_addr}\033[0m")
    if not os.path.exists(LAUNCHER_PATH):
        print(f"    \033[91m[!] Error: Launcher not found at {LAUNCHER_PATH}\033[0m")
        return False
    subprocess.Popen([LAUNCHER_PATH], cwd=os.path.dirname(LAUNCHER_PATH))
    win = find_launcher()
    if not win: 
        print("    \033[91m[!] Failed to find Launcher window.\033[0m")
        return False
    try:
        win.activate()
        win.maximize()
    except Exception as e:
        print(f"    \033[93m[!] Window management warning: {e}\033[0m")
    print("\033[96m[*]\033[0m Task: \033[95mWindow Ready Wait\033[0m")
    countdown("init")
    # 1. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 1 - Click (Change Launcher Login)\033[0m")
    countdown("step-1")
    pyautogui.click(COORDS["step-1"])
    # 2. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 2 - Click (Sign in with different account)\033[0m")
    countdown("step-2")
    pyautogui.click(COORDS["step-2"])
    # 3. scroll
    print("\033[96m[*]\033[0m Task: \033[95mStep 3 - Scroll\033[0m")
    countdown("step-3")
    pyautogui.scroll(-5000)
    # 4. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 4 - Click (Microsoft Account 1)\033[0m")
    countdown("step-4")
    pyautogui.click(COORDS["step-4"])
    # 5. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 5 - Click (Microsoft Account 2)\033[0m")
    countdown("step-5")
    pyautogui.click(COORDS["step-5"])
    # 6. enter email
    print("\033[96m[*]\033[0m Task: \033[95mStep 6 - Enter Email\033[0m")
    countdown("step-6")
    pyautogui.write(email_addr, interval=0.05)
    # 7. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 7 - Click (Next after Email)\033[0m")
    countdown("step-7")
    pyautogui.click(COORDS["step-7"])
    # 8. enter password
    print("\033[96m[*]\033[0m Task: \033[95mStep 8 - Enter Password\033[0m")
    countdown("step-8")
    pyautogui.write(password, interval=0.05)
    pyautogui.press('enter')
    # 9. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 9 - Click (Sign In after Password)\033[0m")
    countdown("step-9")
    pyautogui.click(COORDS["step-9"])
    # 10. enter 2fa email
    print(f"\033[96m[*]\033[0m Task: \033[95mStep 10 - Enter 2FA Recovery Email ({g2_user})\033[0m")
    countdown("step-10")
    pyautogui.write(g2_user, interval=0.05)
    # 11. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 11 - Click (Send 2FA Code)\033[0m")
    countdown("step-11")
    pyautogui.click(COORDS["step-11"])
    # 11b. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 11b - Click (11b)\033[0m")
    countdown("step-11b")
    pyautogui.click(COORDS["step-11b"])
    # 12. enter 2fa code
    print("\033[96m[*]\033[0m Task: \033[95mStep 12 - Enter 2FA Code (Polling...)\033[0m")
    countdown("step-12")
    code = None
    for _ in range(12):
        code = get_2fa_code(g2_user, g2_pass)
        if code: break
        time.sleep(5)
    if code:
        print(f"    \033[92m[>] Typing Code: {code}\033[0m")
        pyautogui.write(code, interval=0.1)
        pyautogui.press('enter')
    else:
        print("    \033[91m[!] No 2FA code found, skipping entry...\033[0m")
    # 13. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 13 - Click (Verify 2FA Code)\033[0m")
    countdown("step-13")
    pyautogui.click(COORDS["step-13"])
    # 14. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 14 - Click (PIN field)\033[0m")
    countdown("step-14")
    pyautogui.click(COORDS["step-14"])
    # 15. enter pin
    print("\033[96m[*]\033[0m Task: \033[95mStep 15 - Enter PIN\033[0m")
    countdown("step-15")
    pyautogui.write(PIN_CODE, interval=0.1)
    pyautogui.press('enter')
    # 16. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 16 - Click (Save and Continue)\033[0m")
    countdown("step-16")
    pyautogui.click(COORDS["step-16"])
    # 17. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 17 - Click (Privacy Step 1)\033[0m")
    countdown("step-17")
    pyautogui.click(COORDS["step-17"])
    # 18. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 18 - Click (Privacy Step 2)\033[0m")
    countdown("step-18")
    pyautogui.click(COORDS["step-18"])
    # 19. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 19 - Click (Let's Go)\033[0m")
    countdown("step-19")
    pyautogui.click(COORDS["step-19"])
    print("\033[96m[*]\033[0m Launching Bedrock...")
    subprocess.run("start minecraft:", shell=True)
    # 20. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 20 - Click (Post-Launch 1)\033[0m")
    countdown("step-20")
    pyautogui.click(COORDS["step-20"])
    # 21. click
    print("\033[96m[*]\033[0m Task: \033[95mStep 21 - Click (Post-Launch 2)\033[0m")
    countdown("step-21")
    pyautogui.click(COORDS["step-21"])
    print("\033[92m[*] Task: Automation Complete. Closing Minecraft...\033[0m")
    time.sleep(10)
    kill_launcher()
    return True

if __name__ == "__main__":
    automate_login("phmmr67730766@outlook.com", "tgwka65949096")
