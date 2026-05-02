import os
import sys
import time
from keyauth import api

def get_auth_config():
    """Load KeyAuth config from .env or use placeholders."""
    config = {
        "name": "",
        "ownerid": "",
        "secret": "",
        "version": "1.0"
    }
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    if key == "KEYAUTH_NAME": config["name"] = value
                    if key == "KEYAUTH_OWNERID": config["ownerid"] = value
                    if key == "KEYAUTH_SECRET": config["secret"] = value
    return config

def authenticate():
    config = get_auth_config()
    
    if not config["name"] or not config["ownerid"]:
        print("\033[91m[!] KeyAuth not configured in .env\033[0m")
        print("Please add KEYAUTH_NAME, KEYAUTH_OWNERID, and KEYAUTH_SECRET to your .env file.")
        time.sleep(5)
        sys.exit(1)

    keyauthapp = api(
        name = config["name"],
        ownerid = config["ownerid"],
        version = config["version"],
        hash_to_check = None
    )

    os.system('cls' if os.name == 'nt' else 'clear')
    print("\033[95m" + "═"*50 + "\033[0m")
    print("\033[94m" + "          AUTHENTICATION REQUIRED          " + "\033[0m")
    print("\033[95m" + "═"*50 + "\033[0m")
    
    # Try to load key from local file to skip prompt
    key_file = "key.txt"
    if os.path.exists(key_file):
        with open(key_file, "r") as f:
            key = f.read().strip()
        print(f"[*] Found saved key. Authenticating...")
    else:
        key = input("\n\033[93m[>] Enter License Key: \033[0m")

    if keyauthapp.license(key):
        print("\033[92m[+] Authentication Successful!\033[0m")
        # Save key for next time
        with open(key_file, "w") as f:
            f.write(key)
        time.sleep(1.5)
        return True
    else:
        print("\033[91m[!] Authentication Failed.\033[0m")
        if os.path.exists(key_file): os.remove(key_file)
        time.sleep(3)
        sys.exit(1)

if __name__ == "__main__":
    authenticate()
