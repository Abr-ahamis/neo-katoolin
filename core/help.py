#!/usr/bin/env python3
import subprocess
import sys
import os

def display_help():
    help_text = """
Neo-Katoolin - Kali Linux Tools Installer
=========================================

OVERVIEW:
Neo-Katoolin is a modular Python-based installer for Kali Linux tools on Ubuntu.
It provides an easy-to-use interface for installing Kali Linux tools, repositories,
and applications.

FEATURES:
1. Add Kali Linux Repository - Adds the official Kali Linux repository to your system
2. Install Default Toolset - Installs all available Kali Linux tools (~400+)
3. Selective Install - Allows you to choose specific categories of tools to install
4. Install Classic Menu Indicator - Adds the Kali Linux menu to your system
5. Install Normal Apps - Installs common applications like Brave, Telegram, etc.
6. Uninstall - Helps you remove installed Kali Linux tools
7. Help & Diagnostics - Provides this help information

USAGE:
- Run main.py to start the installer
- Select an option from the menu by entering the corresponding number
- Follow the on-screen instructions for each option

FILE STRUCTURE:
├── core/
│   ├── apps.py - Installs normal applications
│   ├── classicmenu.py - Installs Kali Linux classic menu
│   ├── default.py - Installs all default Kali Linux tools
│   ├── help.py - Provides help and documentation
│   ├── repo.py - Manages Kali Linux repository
│   ├── Selective.py - Handles category-based installation
│   └── uninstaller.py - Manages uninstallation of tools
├── main.py - Entry point for the application
└── tools/
    └── list-tools.txt - Contains list of all Kali Linux tools

MODULAR DESIGN:
Each component is designed to work independently. You can run any core/*.py script
directly without going through the main menu.

TROUBLESHOOTING:
- Make sure you have an active internet connection
- Run the script with sudo privileges
- Ensure the Kali Linux repository is added before installing tools
- If you encounter errors, check the error messages for specific issues

LICENSE:
This project is open source and released under the MIT License.

CONTRIBUTING:
Contributions are welcome! Please feel free to submit issues and pull requests.
"""
    print(help_text)

def run_diagnostics():
    print("\nRunning diagnostics...")
    
    # Check if running as root
    if os.geteuid() == 0:
        print("✓ Running with root privileges")
    else:
        print("✗ Not running with root privileges (some operations may fail)")
    
    # Check if Kali repository is added
    try:
        with open('/etc/apt/sources.list', 'r') as f:
            content = f.read()
            if 'kali' in content.lower():
                print("✓ Kali Linux repository found")
            else:
                print("✗ Kali Linux repository not found")
    except Exception as e:
        print(f"✗ Error checking repository: {e}")
    
    # Check if tools list exists
    if os.path.exists('tools/list-tools.txt'):
        print("✓ Tools list file found")
    else:
        print("✗ Tools list file not found")
    
    # Check internet connectivity
    try:
        subprocess.run(['ping', '-c', '1', '8.8.8.8'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ Internet connectivity available")
    except:
        print("✗ Internet connectivity not available")
    
    print("\nDiagnostics complete.")

def main():
    print("\n" + "="*50)
    print("Help & Diagnostics")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1) View help documentation")
        print("2) Run diagnostics")
        print("0) Go back to main menu")
        
        choice = input("\nEnter your choice: ")
        
        if choice == '1':
            display_help()
        elif choice == '2':
            run_diagnostics()
        elif choice == '0':
            print("Returning to main menu...")
            return
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()