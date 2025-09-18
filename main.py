#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess

# ===== Color Codes =====
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ===== Root Checker =====
def ensure_root():
    if os.geteuid() != 0:
        print(f"{YELLOW}⚠ This script requires root privileges. Prompting for sudo...{RESET}")
        try:
            subprocess.check_call(['sudo', sys.executable] + sys.argv)
            sys.exit(0)
        except subprocess.CalledProcessError:
            print(f"{RED}❌ Failed to gain root privileges. Exiting.{RESET}")
            sys.exit(1)

# ===== Script Runner =====
def run_script(path):
    if path.endswith(".py"):
        subprocess.run([sys.executable, path])
    elif path.endswith(".sh"):
        subprocess.run(["bash", path])
    else:
        print(f"{RED}⚠ Unsupported script type: {path}{RESET}")

# ===== chmod +x (recursive) =====
def run_chmod():
    print(f"{YELLOW}⚙ Setting execute permission recursively...{RESET}")
    try:
        for root, dirs, files in os.walk("."):
            for filename in files:
                # Check if file is a script type or no extension (likely executable)
                if filename.endswith((".py", ".sh")) or "." not in filename:
                    filepath = os.path.join(root, filename)
                    subprocess.call(["chmod", "+x", filepath])
        print(f"{GREEN}✅ Executable permissions applied to scripts.{RESET}")
    except Exception as e:
        print(f"{RED}❌ chmod failed: {e}{RESET}")

# ===== Get Terminal Width =====
def get_terminal_width():
    try:
        width = shutil.get_terminal_size().columns
        return min(width, 100)
    except Exception:
        return 64  # fallback

# ===== Menu Data =====
ubuntu_options = [
    ("1", "Add Kali repos & update", "core/ubuntu/repo.py"),
    ("2", "Install Kali default tools", "core/both/default.py"),
    ("3", "Custom Installation", "core/both/Selective.py"),
    ("4", "Custom Themes", "core/ubuntu/theme.sh"),
    ("5", "Install common apps", "core/both/apps.py"),
    ("6", "Uninstall tools", "core/both/uninstaller.py"),
    ("7", "Help & diagnostics", "core/ubuntu/help.py"),
    ("0", "Exit", None)
]

kali_options = [
    ("1", "Kali Linux Apps & custom themes", "core/kali/manu.py"),
    ("2", "Add Kali repos & update", "core/kali/repo.py"),
    ("3", "Install Top 10 tools", "core/kali/tools.py"),
    ("4", "Selective install", "core/both/Selective.py"),
    ("5", "Kali custom themes", "core/kali/theme.sh"),
    ("6", "Kali common apps", "core/both/apps.py"),
    ("7", "Uninstall Kali tools", "core/both/uninstaller.py"),
    ("8", "Help & diagnostics", "core/kali/help.py"),
    ("0", "Exit", None)
]

# ===== Draw Menus =====
def draw_header(title):
    width = get_terminal_width()
    print(CYAN + "=" * width + RESET)
    print(f"{BOLD}{GREEN}{title:^{width}}{RESET}")
    print(CYAN + "=" * width + RESET)

def show_menu(options, title="Neo-Katoolin"):
    while True:
        os.system("clear")
        draw_header(title)

        for code, desc, _ in options:
            print(f"{YELLOW}{code}){RESET} {desc}")
        print(CYAN + "=" * get_terminal_width() + RESET)

        try:
            choice = input(f"{MAGENTA}Enter your choice: {RESET}").strip()
        except KeyboardInterrupt:
            print(f"\n{GREEN}Exiting... 👋{RESET}")
            sys.exit(0)

        matched = False
        for code, _, path in options:
            if choice == code:
                matched = True
                if path is None:
                    print(f"{GREEN}Exiting Neo-Katoolin. Goodbye! 👋{RESET}")
                    sys.exit(0)
                run_script(path)
                run_chmod()
                break

        if not matched:
            print(f"{RED}❌ Invalid choice. Try again.{RESET}")
            input(f"{YELLOW}Press Enter to continue...{RESET}")

# ===== Entry Point Menu =====
def main_menu():
    while True:
        os.system("clear")
        draw_header("Neo-Katoolin - Mode Selection")

        print(f"{YELLOW}1){RESET} Ubuntu Mode")
        print(f"{YELLOW}2){RESET} Kali Mode")
        print(f"{YELLOW}0){RESET} Exit")
        print(CYAN + "=" * get_terminal_width() + RESET)

        try:
            mode = input(f"{MAGENTA}Choose a mode: {RESET}").strip()
        except KeyboardInterrupt:
            print(f"\n{GREEN}Exiting... 👋{RESET}")
            sys.exit(0)

        if mode == "1":
            show_menu(ubuntu_options, "Neo-Katoolin - Ubuntu Mode")
        elif mode == "2":
            show_menu(kali_options, "Neo-Katoolin - Kali Mode")
        elif mode == "0":
            print(f"{GREEN}Goodbye! 👋{RESET}")
            sys.exit(0)
        else:
            print(f"{RED}Invalid input. Try again.{RESET}")
            input(f"{YELLOW}Press Enter to continue...{RESET}")

# ===== Launch =====
if __name__ == "__main__":
    ensure_root()
    run_chmod()  # Run chmod once at startup
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Exiting... 👋{RESET}")
        sys.exit(0)
