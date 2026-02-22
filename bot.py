import instaloader
import pyotp
import os
import time
import hashlib
import requests

# ১. ইউনিক ডিভাইস আইডি জেনারেট করা
def get_hwid():
    try:
        id_str = os.getlogin() + "RAKIB_SECURE_2026"
        return hashlib.md5(id_str.encode()).hexdigest()[:10].upper()
    except:
        return "UNKNOWN_ID"

# ২. পারমিশন এবং কী ভেরিফিকেশন
def check_permission():
    hwid = get_hwid()
    print("\n" + "="*46)
    print("======= RAKIB INSTA AUTOMATION =======")
    print("="*46)
    print(f"[*] YOUR DEVICE ID: {hwid}")
    print("-" * 46)

    try:
        url = "https://raw.githubusercontent.com/Rakib40500/insta-auth/refs/heads/main/allow.txt"
        response = requests.get(url)
        authorized_users = {}
        for line in response.text.splitlines():
            if ":" in line:
                u_id, u_key = line.split(":")
                authorized_users[u_id.strip()] = u_key.strip()
    except Exception:
        print("[!] Internet Error! Check connection.")
        return False

    if hwid in authorized_users:
        key = input("[?] ENTER LICENSE KEY: ")
        if key == authorized_users[hwid]:
            print("[SUCCESS] Access Granted!")
            return True
        else:
            print("[ERROR] Wrong Key!"); return False
    else:
        print("[ERROR] Device not registered!"); return False

# ৩. মেইন অটোমেশন (উন্নত ২এফএ সিস্টেমসহ)
def run_automation():
    if not check_permission(): return

    print("\nPaste accounts (User Pass 2FA) then press Enter twice:")
    accounts = []
    while True:
        try:
            line = input()
            if not line.strip(): break
            accounts.append(line.strip())
        except EOFError: break

    output_path = "/sdcard/insta_report.txt"
    for acc in accounts:
        L = instaloader.Instaloader()
        # ব্রাউজারের মতো ইউজার এজেন্ট সেট করা যাতে এরর কম আসে
        L.context.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        try:
            parts = acc.split()
            if len(parts) < 3: continue
            username, password = parts[0], parts[1]
            # ২এফএ কী থেকে সব স্পেস এবং ফালতু ক্যারেক্টার সরানো
            two_fa_key = "".join(parts[2:]).replace(" ", "").upper()

            print(f"\n[*] Working on: {username}")
            
            try:
                L.login(username, password)
            except instaloader.TwoFactorAuthRequiredException:
                # ২এফএ কোড জেনারেট করা (TOTP)
                totp = pyotp.TOTP(two_fa_key)
                current_code = totp.now()
                print(f"[+] 2FA Code Generated: {current_code}")
                L.two_factor_login(current_code)

            # লগইন সফল হলে কুকি সেভ করা
            cookies = L.context._session.cookies.get_dict()
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            with open(output_path, "a") as f:
                f.write(f"{username}|{password}|{cookie_str}\n")
            print(f"[SUCCESS] {username} cookies saved.")
            
        except Exception as e:
            # যদি ২এফএ ভুল হয় বা অন্য কোনো সমস্যা হয়
            error_msg = str(e)
            if "checkpoint" in error_msg.lower():
                print(f"[FAILED] {username}: Security Checkpoint!")
            elif "2fa" in error_msg.lower() or "code" in error_msg.lower():
                print(f"[FAILED] {username}: Invalid 2FA key or code!")
            else:
                print(f"[FAILED] {username}: {error_msg}")
        
        time.sleep(3) # সার্ভার সেফটির জন্য বিরতি

    print(f"\n[DONE] Results saved in: insta_report.txt")

if __name__ == "__main__":
    run_automation()
