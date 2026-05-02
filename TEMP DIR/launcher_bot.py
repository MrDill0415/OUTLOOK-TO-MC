import os
import time
import ctypes
import imaplib
import email
import re
import asyncio
import requests
from ms_login_playwright import MSALoginPlaywright

# Enable ANSI colors for Windows Console
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

DATA_DIR = "accounts_data"
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.txt")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed_accounts.txt")
VALID_TOKENS_FILE = os.path.join(DATA_DIR, "valid_tokens.txt")
TWO_FA_FILE = os.path.join(DATA_DIR, "2fa_required.txt")
INVALID_ACCOUNTS_FILE = os.path.join(DATA_DIR, "invalid_accounts.txt")
ENV_FILE = ".env"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

def load_env():
    env_vars = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
    return env_vars

def get_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    with open(ACCOUNTS_FILE, "r") as f:
        return [line.strip() for line in f if ":" in line]

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        for acc in accounts:
            f.write(f"{acc}\n")

def log_processed(account, status):
    with open(PROCESSED_FILE, "a") as f:
        f.write(f"{account} | STATUS: {status} | TIME: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def get_2fa_code(gmail_user, gmail_pass):
    if gmail_user == "N/A" or gmail_pass == "N/A":
        return None
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
            return code_match.group(0)
        return None
    except Exception:
        return None

def get_xbl_token(access_token):
    url = "https://user.auth.xboxlive.com/user/authenticate"
    payload = {
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": f"d={access_token}"
        }
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data['Token'], data['DisplayClaims']['xui'][0]['uhs']
    except: pass
    return None, None

def get_xsts_token(xbl_token):
    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    payload = {
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT",
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [xbl_token]
        }
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json()['Token']
    except: pass
    return None

def draw_ui(email_addr, password, status_msg, stats=None):
    os.system('cls')
    print(f"{MAGENTA}{BOLD}")
    print("  ▄████████  ███▄▄▄▄      ▄█  ")
    print("  ███    ███  ███▀▀▀██▄   ███  ")
    print("  ███    █▀   ███   ███   ███▌ ")
    print(" ▄███▄▄▄      ███   ███   ███▌ ")
    print("▀▀███▀▀▀      ███   ███   ███▌ ")
    print("  ███    █▄   ███   ███   ███  ")
    print("  ███    ███  ███   ███   ███  ")
    print("  ██████████   ▀█   █▀    █▀   ")
    print(f"       {UNDERLINE}ENI'S XBOX ELITE v6.0{RESET}{MAGENTA}{BOLD}")
    print(f"{RESET}")
    
    print(f"{CYAN}╔══════════════════════════════════════════════════╗{RESET}")
    print(f"{CYAN}║{RESET} {BOLD}{WHITE}ACTIVE SESSION{RESET}                                 {CYAN}║{RESET}")
    print(f"{CYAN}╠══════════════════════════════════════════════════╣{RESET}")
    print(f"{CYAN}║{RESET} {WHITE}TARGET:{RESET} {GREEN}{email_addr.ljust(41)}{RESET}{CYAN}║{RESET}")
    print(f"{CYAN}║{RESET} {WHITE}PASS:  {RESET} {GREEN}{password.ljust(41)}{RESET}{CYAN}║{RESET}")
    if stats:
        print(f"{CYAN}╠══════════════════════════════════════════════════╣{RESET}")
        print(f"{CYAN}║{RESET} {WHITE}PROCESSED:{RESET} {YELLOW}{str(stats['done']).ljust(10)}{RESET} {WHITE}REMAINING:{RESET} {YELLOW}{str(stats['rem']).ljust(11)}{RESET} {CYAN}║{RESET}")
    print(f"{CYAN}╚══════════════════════════════════════════════════╝{RESET}")
    
    # Status Bar
    color = YELLOW if "..." in status_msg or "WAITING" in status_msg else GREEN if "SUCCESS" in status_msg else RED
    print(f"\n {BOLD}{WHITE}[SYSTEM]{RESET} {color}» {status_msg}{RESET}")

from auth_handler import authenticate

async def main():
    authenticate() # KeyAuth Check
    done_count = 0
    try:
        env = load_env()
        g1_user = env.get("GMAIL_USER", "N/A")
        g1_pass = env.get("GMAIL_PASS", "N/A")
        g2_user = env.get("GMAIL_USER_2", "N/A")
        g2_pass = env.get("GMAIL_PASS_2", "N/A")

        bot = MSALoginPlaywright()

        while True:
            accounts = get_accounts()
            if not accounts:
                print(f"\n{GREEN}[+] All accounts processed.{RESET}")
                break

            current_acc = accounts[0]
            parts = current_acc.split(":")
            email_addr = parts[0]
            password = parts[1]
            
            stats = {"done": done_count, "rem": len(accounts)}
            draw_ui(email_addr, password, "INITIALIZING BROWSER...", stats)
            
            success, result = await bot.login(email_addr, password)
            status_to_log = "FAILED"
            
            if success:
                draw_ui(email_addr, password, "LOGIN SUCCESS! EXTRACTING TOKENS...", stats)
                xbl, uhs = get_xbl_token(result)
                if xbl:
                    xsts = get_xsts_token(xbl)
                    if xsts:
                        draw_ui(email_addr, password, "XSTS OBTAINED SUCCESSFULLY", stats)
                        with open(VALID_TOKENS_FILE, "a") as f:
                            f.write(f"{email_addr}:{password}:{xsts}\n")
                        status_to_log = "SUCCESS"
                    else:
                        draw_ui(email_addr, password, "XSTS TOKEN EXCHANGE FAILED", stats)
                        status_to_log = "XSTS_FAIL"
                else:
                    draw_ui(email_addr, password, "XBL TOKEN EXCHANGE FAILED", stats)
                    status_to_log = "XBL_FAIL"
                    
            elif "2FA" in result:
                draw_ui(email_addr, password, "2FA CHALLENGE DETECTED. POLLING GMAIL...", stats)
                code = None
                for _ in range(12):
                    code = get_2fa_code(g1_user, g1_pass) or get_2fa_code(g2_user, g2_pass)
                    if code: break
                    await asyncio.sleep(5)
                
                if code:
                    draw_ui(email_addr, password, f"2FA CODE RETRIEVED: {code}", stats)
                    with open(TWO_FA_FILE, "a") as f:
                        f.write(f"{email_addr}:{password}:{code}\n")
                    status_to_log = f"2FA_PENDING_CODE_{code}"
                else:
                    draw_ui(email_addr, password, "2FA TIMEOUT - NO CODE FOUND", stats)
                    status_to_log = "2FA_TIMEOUT"
            else:
                draw_ui(email_addr, password, f"ERROR: {result}", stats)
                with open(INVALID_ACCOUNTS_FILE, "a") as f:
                    f.write(f"{email_addr}:{password}:{result}\n")
                status_to_log = f"ERROR_{result}"
            
            # Rotation logic
            log_processed(current_acc, status_to_log)
            accounts.pop(0)
            save_accounts(accounts)
            done_count += 1
            
            await asyncio.sleep(3)

    except KeyboardInterrupt:
        print(f"\n{RED}[!] Execution halted by user.{RESET}")
    except Exception as e:
        print(f"\n{RED}[!] CRITICAL ERROR: {e}{RESET}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    asyncio.run(main())
