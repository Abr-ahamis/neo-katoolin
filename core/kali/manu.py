#!/usr/bin/env python3
import os
import sys
import subprocess

# ===== Color Codes =====
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def ensure_root():
    """Re-run the script with sudo if not root."""
    if os.geteuid() != 0:
        print(f"{YELLOW}⚠ This script requires root privileges. Prompting for sudo...{RESET}")
        try:
            subprocess.check_call(['sudo', sys.executable] + sys.argv)
            sys.exit(0)
        except subprocess.CalledProcessError:
            print(f"{RED}❌ Failed to gain root privileges. Exiting.{RESET}")
            sys.exit(1)

def run_script(path):
    """Run a script (.py with Python, .sh with Bash)."""
    if path.endswith(".py"):
        subprocess.run([sys.executable, path])
    elif path.endswith(".sh"):
        subprocess.run(["bash", path])
    else:
        print(f"{RED}⚠ Unsupported script type: {path}{RESET}")

def main_menu():
    while True:
        os.system("clear")  # Clear terminal before showing menu

        print(CYAN + "="*50 + RESET)
        print(f"{BOLD}{GREEN}Kali Linux Apps & custome themes{RESET}")
        print(CYAN + "="*50 + RESET)
        print(f"{YELLOW}1){RESET} Full setup (all apps, themes, grub)")
        print(f"{YELLOW}2){RESET} Install app only")
        print(f"{YELLOW}3){RESET} Setup themes only")
        print(f"{YELLOW}0){RESET} Exit\n")

        try:
            choice = input(f"{MAGENTA}Enter your choice [0-8]: {RESET}")
        except KeyboardInterrupt:
            print(f"\n{GREEN}Exiting Neo-Katoolin. Goodbye! 👋{RESET}")
            sys.exit(0)  # Clean exit on Ctrl+C

        if choice == '1':
            run_script("core/kali/kali_install.sh")
        elif choice == '2':
            run_script("core/kali/app.sh")
        elif choice == '3':
            run_script("core/kali/theme.sh")
        elif choice == '0':
            print(f"{GREEN}Exiting Neo-Katoolin. Goodbye! 👋{RESET}")
            sys.exit(0)
        else:
            print(f"{RED}Invalid choice. Please try again.{RESET}")
            input(f"{YELLOW}Press Enter to continue...{RESET}")  # Pause so error is visible

if __name__ == "__main__":
    ensure_root()
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Exiting Neo-Katoolin. Goodbye! 👋{RESET}")
        sys.exit(0)
