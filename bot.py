import instaloader
import pyotp
import os
import time
import hashlib
import requests
from datetime import datetime

# ১. ইউনিক ডিভাইস আইডি জেনারেট করা
def get_hwid():
    try:
        id_str = os.getlogin() + "RAKIB_SECURE_2026"
        return hashlib.md5(id_str.encode()).hexdigest()[:10].upper()
    except:
        return "UNKNOWN_ID"

# লাইসেন্স কী সেভ রাখার ফাইল পাথ
KEY_FILE = "/data/data/com.termux/files/home/.rakib_key"

# ২. পারমিশন এবং এক্সপায়ারি চেক করা
def check_permission():
    hwid = get_hwid()
    print("\n" + "="*46)
    print("======= RAKIB INSTA AUTOMATION =======")
    print("="*46)
    print(f"[*] YOUR DEVICE ID: {hwid}")
    print("-" * 46)

    saved_key = ""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            saved_key = f.read().strip()

    try:
        # আপনার GitHub raw লিঙ্ক
        url = "https://raw.githubusercontent.com/Rakib40500/insta-auth/refs/heads/main/allow.txt"
        res = requests.get(url).text
        auth_data = {}
        
        for line in res.splitlines():
            if ":" in line:
                # আইডি:কী:তারিখ ফরম্যাট স্প্লিট করা
                parts = [p.strip() for p in line.split(":")]
                if len(parts) >= 2:
                    uid = parts[0]
                    ukey = parts[1]
                    # তারিখ না থাকলে অনেক দূরের তারিখ ধরে নিবে (যেমন অ্যাডমিনদের জন্য)
                    udate = parts[2] if len(parts) >= 3 else "2099-12-30"
                    auth_data[uid] = {"key": ukey, "expiry": udate}
    except Exception:
        print("[!] Network Error! Check your internet.")
        return False

    if hwid in auth_data:
        # মেয়াদ শেষ কি না যাচাই করা
        try:
            expiry_date = datetime.strptime(auth_data[hwid]["expiry"], "%Y-%m-%d")
            if datetime.now() > expiry_date:
                print(f"[!] Access Expired on: {auth_data[hwid]['expiry']}")
                print("[*] Contact Rakib for renewal.")
                return False
        except:
            pass # তারিখ ভুল থাকলে চেক স্কিপ করবে

        # আগে থেকে কী সেভ থাকলে সরাসরি ঢুকবে
        if saved_key == auth_data[hwid]["key"]:
            print(f"[✔] Status: Active | Valid Until: {auth_data[hwid]['expiry']}")
            return True
        
        # নতুন ইউজারের জন্য কী ইনপুট
        key = input("[?] ENTER LICENSE KEY: ")
        if key == auth_data[hwid]["key"]:
            with open(KEY_FILE, "w") as f:
                f.write(key)
            print("[SUCCESS] Access Granted!")
            return True
        else:
            print("[!] Invalid License Key!")
            return False
    
    print("[!] Device not registered!")
    print("[*] Send your ID to Rakib for access.")
    return False

# ৩. মেইন প্রসেসিং ফাংশন
def process_accounts():
    print("\n[>] Paste accounts (User Pass 2FA) & Press Enter twice:")
    accounts = []
    while True:
        try:
            line = input()
            if not line.strip(): break
            accounts.append(line.strip())
        except EOFError:
            break

    if not accounts: return

    output_path = "/sdcard/insta_report.txt"
    for acc in accounts:
        L = instaloader.Instaloader()
        L.context.user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15"
        
        try:
            parts = acc.split()
            if len(parts) < 3: continue
            
            user = parts[0]
            pw = parts[1]
            # সব স্পেস সরিয়ে ২এফএ কী নেওয়া
            fa_key = "".join(parts[2:]).replace(" ", "").upper()
            
            print(f"\n[*] Logging in: {user}")
            try:
                L.login(user, pw)
            except instaloader.TwoFactorAuthRequiredException:
                # অটো ২এফএ কোড জেনারেট
                totp = pyotp.TOTP(fa_key)
                code = totp.now()
                print(f"[+] 2FA Code: {code}")
                L.two_factor_login(code)
            
            # কুকি এক্সট্রাক্ট করা
            cookie = L.context._session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookie.items()])
            
            with open(output_path, "a") as f:
                f.write(f"{user}|{pw}|{cookie_str}\n")
            print(f"[SUCCESS] {user} cookies extracted.")
            
        except Exception as e:
            print(f"[FAILED] {user}: Login Error/2FA Invalid!")
        
        time.sleep(4) # বিরতি
    print("\n[!] Batch complete. Paste more or press Ctrl+C to exit.")

# ৪. রানার
def main():
    if not check_permission():
        return
    
    # অটোমেটিক লুপ যাতে বারবার রান করতে না হয়
    while True:
        process_accounts()
        print("\n" + "="*46)

if __name__ == "__main__":
    main()
