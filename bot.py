import instaloader
import pyotp
import os
import time
import hashlib
import requests

# ১. ডিভাইস আইডি জেনারেট করা
def get_hwid():
    try:
        # প্রতিটি ডিভাইসের জন্য ইউনিক আইডি তৈরি করবে
        id_str = os.getlogin() + "RAKIB_SECURE_2026"
        return hashlib.md5(id_str.encode()).hexdigest()[:10].upper()
    except:
        return "UNKNOWN_ID"

# ২. অনলাইন পারমিশন এবং কী চেক করা
def check_permission():
    hwid = get_hwid()
    print("\n" + "="*46)
    print("======= RAKIB INSTA AUTOMATION =======")
    print("="*46)
    print(f"[*] YOUR DEVICE ID: {hwid}")
    print("-" * 46)

    try:
        # আপনার GitHub-এর raw লিঙ্ক
        url = "https://raw.githubusercontent.com/Rakib40500/insta-auth/refs/heads/main/allow.txt"
        response = requests.get(url)
        
        authorized_users = {}
        # allow.txt ফাইল থেকে ID:KEY ডাটা নেওয়া
        for line in response.text.splitlines():
            if ":" in line:
                u_id, u_key = line.split(":")
                authorized_users[u_id.strip()] = u_key.strip()
    except Exception as e:
        print(f"[ERROR] Internet connection required!")
        return False

    # আইডি লিস্টে আছে কি না দেখা
    if hwid in authorized_users:
        key = input("[?] ENTER LICENSE KEY: ")
        if key == authorized_users[hwid]:
            print("[SUCCESS] Access Granted!")
            time.sleep(1)
            return True
        else:
            print("[ERROR] Wrong Key! Contact Rakib.")
            return False
    else:
        print("[ERROR] Device not registered!")
        print("[*] Send your Device ID to Rakib.")
        return False

# ৩. মেইন অটোমেশন প্রসেস
def run_automation():
    if not check_permission():
        return

    print("\nPaste accounts (User Pass 2FA) then press Enter twice:")
    accounts = []
    while True:
        try:
            line = input()
            if not line.strip(): break
            accounts.append(line.strip())
        except EOFError:
            break

    if not accounts:
        print("[-] No accounts provided!")
        return

    output_path = "/sdcard/insta_report.txt"
    
    for acc in accounts:
        L = instaloader.Instaloader()
        try:
            parts = acc.split()
            if len(parts) < 3: continue
            username, password = parts[0], parts[1]
            # ২এফএ কী থেকে বাড়তি স্পেস রিমুভ করা
            two_fa_key = "".join(parts[2:]).replace(" ", "")

            print(f"\n[*] Working on: {username}")
            
            try:
                L.login(username, password)
            except instaloader.TwoFactorAuthRequiredException:
                # অটোমেটিক ২এফএ কোড জেনারেট এবং সাবমিট
                totp = pyotp.TOTP(two_fa_key)
                L.two_factor_login(totp.now())

            cookies = L.context._session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])

            with open(output_path, "a") as f:
                f.write(f"{username}|{password}|{cookie_str}\n")
            
            print(f"[SUCCESS] {username} cookies saved.")
            time.sleep(2)
        except Exception as e:
            print(f"[FAILED] {username}: {str(e)}")

    print(f"\n[DONE] Check File Manager for: insta_report.txt")

# ৪. মেইন ফাংশন রান করা (এখানেই আপনার এরর ছিল, এখন ঠিক করা হয়েছে)
if _name_ == "_main_":
    run_automation()
