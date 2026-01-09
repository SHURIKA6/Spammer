#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShuraTools.py – Swiss-army knife para spam, banimento e OSINT.
Versão Pro v2.6 Stable
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
{Fore.CYAN} \___ \|  __  |  | |  _  /   / /\ \  
{Fore.CYAN} ____) | |  | | |__| | | \ \  / ____ \ 
{Fore.CYAN}|_____/|_|  |_|\____/|_|  \_\/_/    \_\
                                       
{Fore.YELLOW}  >> SpamMail | OSINT | PortScan | Social <<
{Fore.RED}       v2.6 Stable - by Shura
"""

# ---------- Configurações e Globais ----------
LOCK = threading.Lock()
PROXY_QUEUE = Queue()

UA_LIST = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/19.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
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

# ---------- Módulos de Suporte ----------
def fetch_proxies():
    log("Buscando proxies atualizadas (fontes rápidas)...", "info")
    # Usando fontes de proxies HTTP que costumam ser mais estáveis para POST
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

def run_threads(target_func, qty, threads):
    chunk, rem = qty // threads, qty % threads
    ts = []
    curr = 0
    for i in range(threads):
        take = chunk + (1 if i < rem else 0)
        if take <= 0: continue
        t = threading.Thread(target=target_func, args=(curr, curr + take))
        t.start()
        ts.append(t)
        curr += take
    for t in ts: t.join()

# ---------- Ações Principais ----------
def spam_mail(target, qty, threads, use_proxy):
    # Endpoints variados para não depender de um só
    endpoints = [
        ("https://www.mail-tester.com/contact", {"email": target, "message": "ShuraAttack {rand}"}),
        ("https://newsletter.pudim.com.br/subscribe", {"email": target}),  # Exemplo fictício/comum
        ("https://api.anonfiles.com/mail", {"to": target, "from": "shura@admin.com", "subj": "Alert", "body": "Msg {rand}"})
    ]

    def job(start, end):
        for i in range(start, end):
            mail = fake.email()
            proxies = get_proxy() if use_proxy else None
            # Tenta um endpoint aleatório da lista
            url, data_template = random.choice(endpoints)
            
            # Preenche dados aleatórios se precisar
            data = {}
            for k, v in data_template.items():
                if "{rand}" in str(v): data[k] = v.replace("{rand}", os.urandom(4).hex())
                elif v == target: data[k] = target
                else: data[k] = v

            try:
                headers = {
                    "User-Agent": random.choice(UA_LIST),
                    "Referer": url,
                    "Origin": "/".join(url.split("/")[:3])
                }
                res = requests.post(url, timeout=7, data=data, proxies=proxies, headers=headers)
                if res.status_code in [200, 201, 204]:
                    log(f"Req {i+1} -> OK ({res.status_code})", "success")
                else:
                    log(f"Req {i+1} -> Erro {res.status_code} (Endpoint bloqueou)", "warn")
            except requests.exceptions.ProxyError:
                log(f"Req {i+1} -> Proxy Morta/Lenta", "error")
            except requests.exceptions.Timeout:
                log(f"Req {i+1} -> Timeout (Alvo demorou)", "error")
            except Exception as e:
                log(f"Req {i+1} -> Falha: {str(e)[:40]}...", "error")
                
    run_threads(job, qty, threads)

# (Mantendo OSINT e PortScan mas otimizando logs)
def osint_lookup(target):
    log(f"Investigando pegada digital: {target}", "osint")
    user = target.replace("@", "")
    plats = {
        "Instagram": f"https://www.instagram.com/{user}/",
        "GitHub": f"https://github.com/{user}",
        "X/Twitter": f"https://twitter.com/{user}",
        "TikTok": f"https://www.tiktok.com/@{user}"
    }
    for n, u in plats.items():
        try:
            r = requests.get(u, timeout=5, headers={"User-Agent": random.choice(UA_LIST)})
            if r.status_code == 200: log(f"Encontrado no {n}: {u}", "success")
            else: log(f"Não encontrado no {n}", "info")
        except: pass

def port_scan(target):
    import socket
    log(f"Escaneando portas em {target}...", "osint")
    for port in [21, 22, 25, 53, 80, 443, 3306, 8080]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        if s.connect_ex((target, port)) == 0: log(f"Porta {port} ABERTA", "success")
        s.close()

# ---------- Interface Interativa ----------
def menu_interativo():
    while True:
        clear()
        print(BANNER)
        print(f"{Fore.WHITE}[ 1 ] {Fore.CYAN}Spam de E-mail (Múltiplos Alvos)")
        print(f"{Fore.WHITE}[ 2 ] {Fore.CYAN}Investigação OSINT")
        print(f"{Fore.WHITE}[ 3 ] {Fore.CYAN}Port Scanner (Rede)")
        print(f"{Fore.WHITE}[ 4 ] {Fore.CYAN}Denúncia Social (Zap/IG)")
        print(f"{Fore.WHITE}[ 5 ] {Fore.CYAN}Atualizar Proxies")
        print(f"{Fore.WHITE}[ 0 ] {Fore.RED}Sair do ShuraTools")
        print("-" * 40)
        
        opt = input(f"{Fore.YELLOW}Escolha uma opção: {Style.RESET_ALL}")
        
        if opt == "0": break
        
        if opt in ["1", "2", "3", "4"]:
            target = input(f"{Fore.YELLOW}Digite o alvo (@user, email ou IP): {Style.RESET_ALL}")
            
            if opt == "1":
                try:
                    qty = int(input(f"{Fore.YELLOW}Quantidade (Ex: 20): {Style.RESET_ALL}") or 20)
                    threads = int(input(f"{Fore.YELLOW}Threads (Ex: 5): {Style.RESET_ALL}") or 5)
                    prox = input(f"{Fore.YELLOW}Usar Proxies? (s/n): {Style.RESET_ALL}").lower() == 's'
                    if prox and PROXY_QUEUE.empty(): fetch_proxies()
                    spam_mail(target, qty, threads, prox)
                except ValueError: log("Digite números válidos!", "error")
            
            elif opt == "2": osint_lookup(target)
            elif opt == "3": port_scan(target)
            elif opt == "4": log("Report social em desenvolvimento (Alpha)...", "warn")
            
            input(f"\n{Fore.GREEN}Pressione ENTER para retornar...{Style.RESET_ALL}")
        
        elif opt == "5":
            fetch_proxies()
            input(f"\n{Fore.GREEN}Proxies carregadas. ENTER para voltar...{Style.RESET_ALL}")

def main():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument("--mail", action="store_true")
        parser.add_argument("--osint", action="store_true")
        parser.add_argument("--scan", action="store_true")
        parser.add_argument("--target", required=True)
        parser.add_argument("--qty", type=int, default=10)
        parser.add_argument("--threads", type=int, default=5)
        parser.add_argument("--proxy", action="store_true")
        args = parser.parse_args()
        print(BANNER)
        if args.proxy: fetch_proxies()
        if args.osint: osint_lookup(args.target)
        if args.scan: port_scan(args.target)
        if args.mail: spam_mail(args.target, args.qty, args.threads, args.proxy)
    else:
        menu_interativo()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Operação cancelada.")
