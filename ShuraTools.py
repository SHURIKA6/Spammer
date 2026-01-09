#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v2.7 Anti-Crash
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

# Banner ASCII estilizado
BANNER = f"""
{Fore.CYAN}  _____ _    _ _    _ _____            
{Fore.CYAN} / ____| |  | | |  | |  __ \     /\    
{Fore.CYAN}| (___ | |__| | |  | | |__) |   /  \   
{Fore.CYAN} \___ \|  __  | |  | |  _  /   / /\ \  
{Fore.CYAN} ____) | |  | | |__| | | \ \  / ____ \ 
{Fore.CYAN}|_____/|_|  |_|\____/|_|  \_\/_/    \_\
                                       
{Fore.YELLOW}  >> SpamMail | OSINT | PortScan | Social <<
{Fore.RED}       v2.7 Anti-Crash - by Shura
"""

# ---------- Configurações e Globais ----------
LOCK = threading.Lock()
PROXY_QUEUE = Queue()

UA_LIST = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/19.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Instagram 350.0.0.50.110 Android (34/14; 560dpi; 1440x3120; Google; Pixel 9; en_US; 620211153)"
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

def fetch_proxies():
    log("Buscando proxies atualizadas...", "info")
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
    log(f"{count} proxies carregadas.", "success")

def get_proxy():
    if PROXY_QUEUE.empty(): return None
    p = PROXY_QUEUE.get()
    PROXY_QUEUE.put(p)
    return {"http": f"http://{p}", "https": f"http://{p}"}

# ---------- Ações ----------
def spam_mail(target, qty, threads, use_proxy):
    endpoints = [
        ("https://www.mail-tester.com/contact", {"email": target, "message": "ShuraAttack {rand}"}),
        ("https://api.anonfiles.com/mail", {"to": target, "from": "shura@admin.com", "subj": "Alert", "body": "Msg {rand}"})
    ]
    def job(start, end):
        for i in range(start, end):
            try:
                proxies = get_proxy() if use_proxy else None
                url, data_template = random.choice(endpoints)
                data = {k: (v.replace("{rand}", os.urandom(4).hex()) if "{rand}" in str(v) else v) for k, v in data_template.items()}
                res = requests.post(url, timeout=7, data=data, proxies=proxies, headers={"User-Agent": random.choice(UA_LIST)})
                log(f"Req {i+1} -> Status {res.status_code}", "success" if res.status_code < 400 else "warn")
            except Exception:
                log(f"Req {i+1} -> Falha na conexão", "error")
    
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
    try:
        log(f"Investigando: {target}", "osint")
        user = target.replace("@", "")
        plats = {"Instagram": f"https://www.instagram.com/{user}/", "GitHub": f"https://github.com/{user}"}
        for n, u in plats.items():
            try:
                r = requests.get(u, timeout=5, headers={"User-Agent": random.choice(UA_LIST)})
                log(f"{n}: {'ENCONTRADO' if r.status_code == 200 else 'Não encontrado'}", "success" if r.status_code == 200 else "info")
            except: pass
    except Exception as e:
        log(f"Erro no OSINT: {e}", "error")

def port_scan(target):
    log(f"Escaneando portas em {target}...", "osint")
    try:
        # Resolve o host primeiro para validar
        resolved_ip = socket.gethostbyname(target)
        log(f"IP Resolvido: {resolved_ip}", "info")
        for port in [21, 22, 53, 80, 443, 3306, 8080]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.2)
            if s.connect_ex((resolved_ip, port)) == 0:
                log(f"Porta {port} ABERTA", "success")
            s.close()
    except socket.gaierror:
        log("Erro: Alvo ou domínio inválido (getaddrinfo failed).", "error")
    except Exception as e:
        log(f"Erro no PortScan: {e}", "error")

# ---------- Menu ----------
def menu_interativo():
    while True:
        try:
            clear()
            print(BANNER)
            print(f"[ 1 ] Spam de E-mail")
            print(f"[ 2 ] Investigação OSINT")
            print(f"[ 3 ] Port Scanner (Rede)")
            print(f"[ 5 ] Atualizar Proxies")
            print(f"[ 0 ] Sair")
            print("-" * 40)
            
            opt = input(f"{Fore.YELLOW}Opção: {Style.RESET_ALL}").strip()
            
            if opt == "0": break
            if opt == "5": fetch_proxies(); input("\nENTER..."); continue
            
            if opt in ["1", "2", "3"]:
                target = input(f"{Fore.YELLOW}Alvo: {Style.RESET_ALL}").strip()
                if not target: continue
                
                if opt == "1":
                    qty = safe_int(f"{Fore.YELLOW}Quantidade (10): ", 10)
                    threads = safe_int(f"{Fore.YELLOW}Threads (5): ", 5)
                    prox = input(f"{Fore.YELLOW}Usar Proxies? (s/n): {Style.RESET_ALL}").lower() == 's'
                    if prox and PROXY_QUEUE.empty(): fetch_proxies()
                    spam_mail(target, qty, threads, prox)
                
                elif opt == "2": osint_lookup(target)
                elif opt == "3": port_scan(target)
                
                input(f"\n{Fore.GREEN}Pressione ENTER para continuar...{Style.RESET_ALL}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"Ocorreu um erro inesperado: {e}", "error")
            input("\nENTER para resetar...")

if __name__ == "__main__":
    menu_interativo()
