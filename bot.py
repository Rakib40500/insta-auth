import instaloader
import pyotp
import os
import time
import hashlib
import requests

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
        auth = {}
        for line in res.splitlines():
            if ":" in line:
                uid, ukey = line.split(":")
                auth[uid.strip()] = ukey.strip()
    except: return False
    if hwid in auth:
        if saved_key == auth[hwid]: return True
        key = input("[?] ENTER LICENSE KEY: ")
        if key == auth[hwid]:
            with open(KEY_FILE, "w") as f: f.write(key)
            return True
    return False

def run_automation():
    if not check_permission(): print("[!] Access Denied!"); return
    print("\nPaste accounts (User Pass 2FA) - Example: user pass key")
    print("Press Enter twice to start...")
    accounts = []
    while True:
        try:
            line = input()
            if not line.strip(): break
            accounts.append(line.strip())
        except: break

    output_path = "/sdcard/insta_report.txt"
    for acc in accounts:
        L = instaloader.Instaloader()
        L.context.user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15"
        try:
            # এখানে স্পেস বড় হোক বা ছোট, সব ঠিক করে নিবে
            parts = acc.split()
            if len(parts) < 3:
                print(f"[!] Invalid Format: {acc}")
                continue
            
            user = parts[0] # প্রথম শব্দ ইউজারনেম
            pw = parts[1]   # দ্বিতীয় শব্দ পাসওয়ার্ড
            # বাকি সব স্পেস রিমুভ করে ২এফএ কী বানানো হচ্ছে
            fa_key = "".join(parts[2:]).replace(" ", "").upper()
            
            print(f"\n[*] Working on: {user}")
            try:
                L.login(user, pw)
            except instaloader.TwoFactorAuthRequiredException:
                totp = pyotp.TOTP(fa_key)
                code = totp.now()
                print(f"[+] Auto 2FA Code Generated: {code}")
                L.two_factor_login(code)
            
            cookie = L.context._session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookie.items()])
            with open(output_path, "a") as f:
                f.write(f"{user}|{pw}|{cookie_str}\n")
            print(f"[SUCCESS] {user} saved to report.")
        except Exception as e:
            print(f"[FAILED] {user}: Login Error/2FA Invalid!")
        
        print("-" * 30)
        time.sleep(5) # অটোমেটিক পরের অ্যাকাউন্টে যাওয়ার জন্য
    
    print(f"\n[DONE] Results saved in: insta_report.txt")

if __name__ == "__main__":
    run_automation()
