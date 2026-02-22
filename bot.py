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

def check_permission():
    hwid = get_hwid()
    print("\n" + "="*46 + "\n======= RAKIB INSTA AUTOMATION =======\n" + "="*46)
    print(f"[*] YOUR DEVICE ID: {hwid}\n" + "-" * 46)
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
        key = input("[?] ENTER LICENSE KEY: ")
        if key == auth[hwid]: return True
    return False

def run_automation():
    if not check_permission(): print("[!] Access Denied!"); return
    print("\nPaste accounts (User Pass 2FA) then press Enter twice:")
    accounts = []
    while True:
        try:
            line = input(); 
            if not line.strip(): break
            accounts.append(line.strip())
        except: break

    output_path = "/sdcard/insta_report.txt"
    for acc in accounts:
        L = instaloader.Instaloader()
        # ব্রাউজারের মতো এজেন্ট সেট করা যাতে এরর কম আসে
        L.context.user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
        try:
            parts = acc.split()
            if len(parts) < 3: continue
            user, pw = parts[0], parts[1]
            # ২এফএ কী থেকে সব স্পেস সরিয়ে দেওয়া হচ্ছে যাতে কোড ভুল না আসে
            fa_key = "".join(parts[2:]).replace(" ", "").upper()
            print(f"\n[*] Working on: {user}")
            try:
                L.login(user, pw)
            except instaloader.TwoFactorAuthRequiredException:
                # অটোমেটিক ২এফএ কোড জেনারেট করা
                totp = pyotp.TOTP(fa_key)
                code = totp.now()
                print(f"[+] 2FA Code Generated: {code}")
                L.two_factor_login(code)
            
            cookie = L.context._session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookie.items()])
            with open(output_path, "a") as f:
                f.write(f"{user}|{pw}|{cookie_str}\n")
            print(f"[SUCCESS] {user} cookies saved.")
        except Exception as e:
            msg = str(e)
            if "checkpoint" in msg.lower(): print(f"[FAILED] {user}: Security Checkpoint!")
            else: print(f"[FAILED] {user}: Login Error/2FA Invalid!")
        time.sleep(5) # ৫ সেকেন্ড বিরতি যাতে ব্লক না খায়
    print(f"\n[DONE] Check: insta_report.txt")

if __name__ == "__main__":
    run_automation()
