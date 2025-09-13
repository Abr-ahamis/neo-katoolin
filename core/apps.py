#!/usr/bin/env python3
import subprocess
import os
import sys

# Find the absolute path to the tools directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")

def execute_bash(script_name):
    """Execute a Bash script from the tools directory"""
    script_path = os.path.join(TOOLS_DIR, script_name)

    if not os.path.isfile(script_path):
        print(f"Error: {script_path} not found!")
        return

    if not os.access(script_path, os.X_OK):
        print(f"Making {script_path} executable...")
        os.chmod(script_path, 0o755)

    try:
        subprocess.run([script_path], check=True)
        input("\n✅ Done. Press Enter to return to menu...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing {script_path}: {e}")

def display_menu():
    print("\n" + "="*50)
    print("Neo-Katoolin - Applications Installer Menu")
    print("="*50)
    print("1) Install Brave Browser")
    print("2) Install Telegram Desktop")
    print("3) Install Visual Studio Code")
    print("4) Install ProtonVPN")
    print("00) Install All Applications")
    print("0) Exit")

def main():
    if os.geteuid() != 0:
        print("⚠️  This script requires root privileges. Please run with sudo.")
        return

    while True:
        display_menu()
        choice = input("\nEnter your choice: ").strip()

        if choice == '0':
            print("Exiting Applications Installer. Goodbye!")
            break
        elif choice == '1':
            execute_bash("install_brave.sh")
        elif choice == '2':
            execute_bash("install_telegram.sh")
        elif choice == '3':
            execute_bash("install_vscode.sh")
        elif choice == '4':
            execute_bash("install_protonvpn.sh")
        elif choice == '00':
            for script in [
                "install_brave.sh",
                "install_telegram.sh",
                "install_vscode.sh",
                "install_protonvpn.sh"
            ]:
                execute_bash(script)
        else:
            print("Invalid choice. Please enter a valid number.")

if __name__ == "__main__":
    main()
