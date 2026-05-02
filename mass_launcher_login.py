import os
import time
import ctypes
from ui_automation import automate_login

# Enable ANSI colors for Windows Console
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

DATA_DIR = "accounts_data"
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.txt")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed_ui_accounts.txt")

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

def draw_header(email="", current=0, total=0):
    os.system('cls')
    print(f"{CYAN}{BOLD}")
    print("  ▄████████  ███▄▄▄▄      ▄█  ")
    print("  ███    ███  ███▀▀▀██▄   ███  ")
    print("  ███    █▀   ███   ███   ███▌ ")
    print(" ▄███▄▄▄      ███   ███   ███▌ ")
    print("▀▀███▀▀▀      ███   ███   ███▌ ")
    print("  ███    █▄   ███   ███   ███  ")
    print("  ███    ███  ███   ███   ███  ")
    print("  ██████████   ▀█   █▀    █▀   ")
    print(f"       {UNDERLINE}MASS UI-LOGIN ELITE v6.0{RESET}{CYAN}{BOLD}")
    print(f"{RESET}")
    
    if email:
        print(f"{MAGENTA}╔══════════════════════════════════════════════════╗{RESET}")
        print(f"{MAGENTA}║{RESET} {BOLD}{WHITE}UI AUTOMATION IN PROGRESS{RESET}                      {MAGENTA}║{RESET}")
        print(f"{MAGENTA}╠══════════════════════════════════════════════════╣{RESET}")
        print(f"{MAGENTA}║{RESET} {WHITE}ACCOUNT:{RESET} {YELLOW}{str(current).rjust(2)}/{str(total).ljust(2)}{RESET}                                {MAGENTA}║{RESET}")
        print(f"{MAGENTA}║{RESET} {WHITE}TARGET: {RESET} {CYAN}{email.ljust(41)}{RESET}{MAGENTA}║{RESET}")
        print(f"{MAGENTA}╚══════════════════════════════════════════════════╝{RESET}")

from auth_handler import authenticate

def main():
    authenticate() # KeyAuth Check
    done_count = 0
    while True:
        accounts = get_accounts()
        if not accounts:
            draw_header()
            print(f"{GREEN}[+] All accounts processed.{RESET}")
            break

        total = len(accounts) + done_count
        current_acc = accounts[0]
        email, password = current_acc.split(":")
        
        draw_header(email, done_count + 1, total)
        
        try:
            success = automate_login(email, password)
            if success:
                print(f"\n{GREEN}[+] Success! Bedrock launched with {email}{RESET}")
                log_processed(current_acc, "SUCCESS")
            else:
                print(f"\n{RED}[X] Automation failed for {email}{RESET}")
                log_processed(current_acc, "FAILED")
        except Exception as e:
            print(f"\n{RED}[!] Fatal Error: {e}{RESET}")
            log_processed(current_acc, f"ERROR: {str(e)}")

        # Rotation
        accounts.pop(0)
        save_accounts(accounts)
        done_count += 1
        
        print(f"\n{YELLOW}[*] Cool-down... Next account in 5s{RESET}")
        time.sleep(5)

if __name__ == "__main__":
    main()
