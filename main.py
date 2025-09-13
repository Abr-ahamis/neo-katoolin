#!/usr/bin/env python3
import os
import sys
import subprocess

def ensure_root():
    """Re-run the script with sudo if not root."""
    if os.geteuid() != 0:
        print("⚠ This script requires root privileges. Prompting for sudo...")
        try:
            # Re-run the current script with sudo
            subprocess.check_call(['sudo', sys.executable] + sys.argv)
            sys.exit(0)  # exit the current non-root instance
        except subprocess.CalledProcessError:
            print("❌ Failed to gain root privileges. Exiting.")
            sys.exit(1)

def main_menu():
    while True:
        print("\n" + "="*50)
        print("Neo-Katoolin - Kali Linux Tools Installer")
        print("="*50)
        print("1) Add Kali repo & update")
        print("2) Install default toolset")
        print("3) Selective install (categories)")
        print("4) Install classicmenu indicator")
        print("5) Install normal apps")
        print("6) Uninstall")
        print("7) Help & diagnostics")
        print("8) Exit")
        
        choice = input("\nEnter your choice [1-8]: ")
        
        if choice == '1':
            subprocess.run([sys.executable, 'core/repo.py'])
        elif choice == '2':
            subprocess.run([sys.executable, 'core/default.py'])
        elif choice == '3':
            subprocess.run([sys.executable, 'core/Selective.py'])
        elif choice == '4':
            subprocess.run([sys.executable, 'core/classicmenu.py'])
        elif choice == '5':
            subprocess.run([sys.executable, 'core/apps.py'])
        elif choice == '6':
            subprocess.run([sys.executable, 'core/uninstaller.py'])
        elif choice == '7':
            subprocess.run([sys.executable, 'core/help.py'])
        elif choice == '8':
            print("Exiting Neo-Katoolin. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    ensure_root()
    main_menu()
