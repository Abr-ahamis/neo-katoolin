#!/usr/bin/env python3
import subprocess
import sys
import os

def install_classicmenu():
    try:
        print("Installing Kali Linux classic menu indicator...")
        subprocess.run(['apt-get', 'install', '-y', 'kali-menu'], check=True)
        print("Kali Linux classic menu indicator installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing classic menu indicator: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("Install Kali Linux Classic Menu Indicator")
    print("="*50)
    
    if os.geteuid() != 0:
        print("This script requires root privileges. Please run with sudo.")
        return
    
    print("This will install the Kali Linux classic menu indicator.")
    print("The classic menu provides easy access to Kali Linux tools.")
    
    confirm = input("Continue? (y/n): ")
    if confirm.lower() == 'y':
        if install_classicmenu():
            print("Classic menu indicator installed successfully!")
        else:
            print("Failed to install classic menu indicator.")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()