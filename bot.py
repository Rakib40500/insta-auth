import os, hashlib, requests, pyotp, instaloader, time
from datetime import datetime

# ১. ইউনিক ডিভাইস আইডি জেনারেট করা
def get_hwid():
    try:
        id_str = os.getlogin() + "RAKIB_SECURE_2026"
        return hashlib.md5(id_str.encode()).hexdigest()[:10].upper()
    except: return "UNKNOWN_ID"

# ২. পারমিশন চেক (GitHub থেকে)
def check_permission():
    hwid = get_hwid()
    print("\n" + "="*46 + "\n======= RAKIB INSTA AUTOMATION =======\n" + "="*46)
    print(f"[*] YOUR DEVICE ID: {hwid}\n" + "-" * 46)
    
    try:
        url = "https://raw.githubusercontent.com/Rakib40500/insta-auth/refs/heads/main/allow.txt"
        res = requests.get(url).text
        auth_data = {}
        for line in res.splitlines():
            if ":" in line:
                parts = [p.strip() for p in line.split(":")]
                if len(parts) >= 2:
                    auth_data[parts[0]] = {"key": parts[1], "expiry": parts[2] if len(parts) >= 3 else "2099-12-30"}
    except: print("[!] Network Error!"); return False

    if hwid in auth_data:
        expiry = datetime.strptime(auth_data[hwid]["expiry"], "%Y-%m-%d")
        if datetime.now() > expiry:
            print("[!] Access Expired!"); return False
        print(f"[✔] Status: Active | Valid Until: {auth_data[hwid]['expiry']}")
        return True
    
    print("[!] Device not registered!"); return False

if __name__ == "__main__":
    if check_permission():
        print("[*] Access Granted. Start your work...")
        # এখানে আপনার মূল কাজ শুরু হবে...
