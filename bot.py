import instaloader
import pyotp
import os
import time
import hashlib
import requests
from datetime import datetime

def get_hwid():
    try:
        id_str = os.getlogin() + "RAKIB_SECURE_2026"
        return hashlib.md5(id_str.encode()).hexdigest()[:10].upper()
    except: return "UNKNOWN_ID"

KEY_FILE = "/data/data/com.termux/files/home/.rakib_key"

def check_permission():
    hwid = get_hwid()
    print("\n" + "="*46 + "\n======= RAKIB INSTA AUTOMATION =======\n" + "="*46)
    print(f"[*] YOUR DEVICE ID: {hwid}\n" + "-" * 46)
    
    saved_key = ""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f: saved_key = f.read().strip()
    
    try:
        url = "https://raw.githubusercontent.com/Rakib40500/insta-auth/refs/heads/main/allow.txt"
        res = requests.get(url).text
        auth_data = {}
        for line in res.splitlines():
            if ":" in line:
                parts = line.split(":")
                if len(parts) >= 3:
                    uid, ukey, udate = parts[0].strip(), parts[1].strip(), parts[2].strip()
                    auth_data[uid] = {"key": ukey, "expiry": udate}
    except: return False

    if hwid in auth_data:
        # মেয়াদ শেষ কি না চেক করা
        expiry_date = datetime.strptime(auth_data[hwid]["expiry"], "%Y-%m-%d")
        if datetime.now() > expiry_date:
            print(f"[!] Access Expired on: {auth_data[hwid]['expiry']}")
            print("[*] Contact Rakib to renew.")
            return False

        if saved_key == auth_data[hwid]["key"]:
            print(f"[✔] License Valid Until: {auth_data[hwid]['expiry']}")
            return True
        
        key = input("[?] ENTER LICENSE KEY: ")
        if key == auth_data[hwid]["key"]:
            with open(KEY_FILE, "w") as f: f.write(key)
            return True
    
    print("[!] Device not registered or Access Denied!")
    return False

def process_accounts():
    print("\n[>] Paste accounts (User Pass 2FA) & Press Enter twice:")
    accounts = []
    while True:
        try:
            line = input()
            if not line.strip(): break
            accounts.append(line.strip())
        except: break

    if not accounts: return

    output_path = "/sdcard/insta_report.txt"
    for acc in accounts:
        L = instaloader.Instaloader()
        L.context.user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15"
        try:
            parts = acc.split()
            if len(parts) < 3: continue
            user, pw = parts[0], parts[1]
            fa_key = "".join(parts[2:]).replace(" ", "").upper()
            
            print(f"\n[*] Logging in: {user}")
            try:
                L.login(user, pw)
            except instaloader.TwoFactorAuthRequiredException:
                code = pyotp.TOTP(fa_key).now()
                print(f"[+] 2FA Code: {code}")
                L.two_factor_login(code)
            
            cookie = L.context._session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookie.items()])
            with open(output_path, "a") as f:
                f.write(f"{user}|{pw}|{cookie_str}\n")
            print(f"[SUCCESS] {user} cookies extracted.")
        except Exception:
            print(f"[FAILED] {user}: Check Pass/2FA Key!")
        time.sleep(4)
    print("\n[!] Batch complete.")

def main():
    if not check_permission(): return
    while True:
        process_accounts()
        print("\n" + "="*40)

if __name__ == "__main__":
    main()
