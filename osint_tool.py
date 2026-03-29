import sys
import os
import subprocess
import io
import random
import string
from datetime import datetime

def install_requirements():
    requirements = ['requests', 'python-whois', 'phonenumbers', 'colorama']
    for lib in requirements:
        try:
            __import__(lib.replace('python-', ''))
        except ImportError:
            print(f"[*] Installing missing library: {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_requirements()

import requests
import whois
import phonenumbers
from phonenumbers import carrier, geocoder
from colorama import Fore, init

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
init(autoreset=True)

LOG_FILE = "report.txt"
SHERLOCK_DIR = os.path.join(os.getcwd(), "sherlock")
current_lang = 'en'
LANGS = {
    'en': {
        'title': "Osint Tool | Version 1.0",
        'menu_1': "1. Sherlock (Nickname)",
        'menu_2': "2. IP Lookup (Target)",
        'menu_3': "3. Phone Lookup",
        'menu_4': "4. WHOIS Domain",
        'menu_5': "5. My IP / VPN",
        'menu_6': "6. Nickname Gen",
        'menu_7': "7. Change Language",
        'menu_8': "8. Clear Logs",
        'menu_0': "0. Exit",
        'select_lang_text': "Select Language:",
        'enter_nick': "Enter nickname: ",
        'searching': "[*] Searching accounts for: ",
        'no_folder': "[-] Folder not found. Git clone required.",
        'my_ip_info': "[*] Checking your IP...",
        'proxy_warn': "[!] Warning: Proxy or VPN detected!",
        'direct_warn': "[i] You are using a direct connection.",
        'gen_title': "[*] Nickname Generator",
        'gen_base': "Enter base (or Enter for random): ",
        'done': "[+] Done!"
    },
    'uk': {
        'title': "Osint Інструмент | Версія 1.0",
        'menu_1': "1. Sherlock (Нікнейм)",
        'menu_2': "2. IP Lookup (Ціль)",
        'menu_3': "3. Phone Lookup",
        'menu_4': "4. WHOIS Domain",
        'menu_5': "5. Мій IP / VPN",
        'menu_6': "6. Генератор ніків",
        'menu_7': "7. Змінити мову",
        'menu_8': "8. Очистити звіти",
        'menu_0': "0. Вихід",
        'select_lang_text': "Оберіть мову:",
        'enter_nick': "Введіть нікнейм: ",
        'searching': "[*] Пошук акаунтів для: ",
        'no_folder': "[-] Папку не знайдено. Потрібен git clone.",
        'my_ip_info': "[*] Перевірка вашого IP...",
        'proxy_warn': "[!] Увага: Виявлено проксі або VPN!",
        'direct_warn': "[i] Ви сидите з прямої адреси (без VPN).",
        'gen_title': "[*] Генератор нікнеймів",
        'gen_base': "Введіть основу (або Enter для рандому): ",
        'done': "[+] Готово!"
    },
    'ru': {
        'title': "Osint Инструмент | Версия 1.0",
        'menu_1': "1. Sherlock (Никнейм)",
        'menu_2': "2. IP Lookup (Цель)",
        'menu_3': "3. Phone Lookup",
        'menu_4': "4. WHOIS Domain",
        'menu_5': "5. Мой IP / VPN",
        'menu_6': "6. Генератор ников",
        'menu_7': "7. Сменить язык",
        'menu_8': "8. Очистить отчеты",
        'menu_0': "0. Выход",
        'select_lang_text': "Выберите язык:",
        'enter_nick': "Введите никнейм: ",
        'searching': "[*] Поиск аккаунтов для: ",
        'no_folder': "[-] Папка не найдена. Нужен git clone.",
        'my_ip_info': "[*] Проверка вашего IP...",
        'proxy_warn': "[!] Внимание: Обнаружен прокси или VPN!",
        'direct_warn': "[i] Вы зашли с прямого адреса (без VPN).",
        'gen_title': "[*] Генератор никнеймов",
        'gen_base': "Введите основу (или Enter для рандома): ",
        'done': "[+] Готово!"
    }
}

def t(key):
    return LANGS[current_lang].get(key, key)

def log_to_file(category, target, data):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n{'='*50}\n[{time_str}] {category}\nTARGET: {target}\n{data}\n{'='*50}\n")
    except: pass

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "="*65)
    print(Fore.YELLOW + f"          {t('title')}")
    print(Fore.CYAN + "="*65)

def change_language():
    global current_lang
    print(f"\n{t('select_lang_text')}")
    print("1. English")
    print("2. Українська")
    print("3. Русский")
    c = input(">>> ")
    if c == '1': current_lang = 'en'
    elif c == '2': current_lang = 'uk'
    elif c == '3': current_lang = 'ru'

def run_sherlock():
    user = input(f"{Fore.YELLOW}{t('enter_nick')}{Fore.WHITE}")
    if not os.path.exists(SHERLOCK_DIR):
        print(Fore.RED + t('no_folder'))
        return
    print(Fore.GREEN + f"{t('searching')} {user}")
    env = os.environ.copy()
    env["PYTHONPATH"] = SHERLOCK_DIR + os.pathsep + env.get("PYTHONPATH", "")
    cmd = [sys.executable, "-m", "sherlock_project", user, "--timeout", "5"]
    try:
        process = subprocess.Popen(cmd, cwd=SHERLOCK_DIR, stdout=subprocess.PIPE, text=True, encoding='utf-8', env=env)
        results = []
        for line in process.stdout:
            print(line.strip())
            if "[+]" in line: results.append(line.strip())
        process.wait()
        if results: log_to_file("SHERLOCK", user, "\n".join(results))
    except Exception as e: print(Fore.RED + f"Error: {e}")

def check_my_ip():
    print(Fore.CYAN + t('my_ip_info'))
    try:
        r = requests.get("http://ip-api.com/json/?fields=status,country,city,isp,query,proxy").json()
        if r.get('status') == 'success':
            print(Fore.BLUE + f"IP: {r.get('query')} ({r.get('city')}, {r.get('country')})")
            print(Fore.BLUE + f"ISP: {r.get('isp')}")
            print(Fore.RED + t('proxy_warn') if r.get('proxy') else Fore.YELLOW + t('direct_warn'))
    except: print(Fore.RED + "Error")

def nickname_gen():
    print(Fore.CYAN + t('gen_title'))
    base = input(f"{Fore.YELLOW}{t('gen_base')}{Fore.WHITE}")
    suffixes = ["_osint", "root", "_cyber", "shadow", "void", "x"]
    for _ in range(5):
        name = (base if base else "".join(random.choices(string.ascii_lowercase, k=6))) + random.choice(suffixes) + str(random.randint(1, 99))
        print(f" > {name}")

def ip_lookup():
    ip = input("IP: ")
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        data = f"Loc: {r.get('city')}, {r.get('country')}\nISP: {r.get('isp')}"
        print(Fore.BLUE + data)
        log_to_file("IP", ip, data)
    except: print(Fore.RED + "Error")

def phone_lookup():
    num = input("Phone (+1...): ")
    try:
        p = phonenumbers.parse(num)
        data = f"Reg: {geocoder.description_for_number(p, 'uk')}\nOp: {carrier.name_for_number(p, 'uk')}"
        print(Fore.BLUE + data)
        log_to_file("PHONE", num, data)
    except: print(Fore.RED + "Error")

def main():
    while True:
        print_header()
        print(t('menu_1'))
        print(t('menu_2'))
        print(t('menu_3'))
        print(t('menu_4'))
        print(t('menu_5'))
        print(t('menu_6'))
        print(f"{Fore.MAGENTA}{t('menu_7')}")
        print(t('menu_8'))
        print(f"{Fore.RED}{t('menu_0')}")
        
        choice = input(f"\n{Fore.YELLOW}>>> {Fore.WHITE}")
        
        if choice == '1': run_sherlock()
        elif choice == '2': ip_lookup()
        elif choice == '3': phone_lookup()
        elif choice == '4': 
            dom = input("Domain: ")
            try: print(Fore.BLUE + str(whois.whois(dom).registrar))
            except: pass
        elif choice == '5': check_my_ip()
        elif choice == '6': nickname_gen()
        elif choice == '7': change_language()
        elif choice == '8':
            open(LOG_FILE, "w").close()
            print(t('done'))
        elif choice == '0': break
        input("\n[Enter]...")

if __name__ == "__main__":
    main()
