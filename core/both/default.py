#!/usr/bin/env python3
import subprocess
import sys
import os
import shutil

def get_tools_list():
    """Read tools from the list-tools.txt file"""
    try:
        with open('core/tools/list-tools.txt', 'r') as f:
            tools = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return tools
    except FileNotFoundError:
        print("Error: core/tools/list-tools.txt not found.")
        return []
    except Exception as e:
        print(f"Error reading tools list: {e}")
        return []

def is_installed(tool):
    """Check if a tool is already installed in the system"""
    return shutil.which(tool) is not None

def run_command(cmd):
    """Run a shell command and return True if successful"""
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def install_tool(tool):
    """Install a single tool with apt-get, fallback to snap"""
    if is_installed(tool):
        return "skipped"

    # Try apt-get
    if run_command(['apt-get', 'install', '-y', tool]):
        return "installed"

    # Fallback to snap
    if run_command(['snap', 'install', tool]):
        return "installed_snap"

    return "failed"

def install_tools(tools):
    """Install all tools from the list with a clean progress display"""
    total = len(tools)
    success_count = 0
    failed_tools = []

    print(f"\n📦 Installing {total} tools...\n")

    for idx, tool in enumerate(tools, 1):
        try:
            status = install_tool(tool)

            # Display clean progress
            progress_percent = int((idx / total) * 100)
            status_display = {
                "installed": "✅",
                "installed_snap": "✅ (snap)",
                "skipped": "✔ already installed",
                "failed": "❌ failed"
            }
            print(f"[{progress_percent:3}%] ({idx}/{total}) {tool} {status_display[status]}")

            # Count successes/failures
            if status in ["installed", "installed_snap"]:
                success_count += 1
            elif status == "failed":
                failed_tools.append(tool)

        except KeyboardInterrupt:
            # Handle Ctrl+C to stop installation
            print("\n\nOperation interrupted by user. Exiting gracefully...")
            break
        except EOFError:
            # Handle Ctrl+D to stop installation
            print("\n\nOperation stopped by user (Ctrl+D). Exiting gracefully...")
            break

    # Summary
    print("\n" + "="*40)
    print("   📊 Installation Summary")
    print("="*40)
    print(f"✅ Successfully installed: {success_count}")
    print(f"❌ Failed to install: {len(failed_tools)}")
    if failed_tools:
        print("\nFailed tools:")
        for t in failed_tools:
            print(f" - {t}")

def main():
    print("\n" + "="*50)
    print("⚡ Pro Kali Linux Tool Installer")
    print("="*50)

    if os.geteuid() != 0:
        print("This script requires root privileges. Please run with sudo.")
        return

    tools = get_tools_list()
    if not tools:
        print("No tools found in the list. Exiting.")
        return

    print(f"This will install {len(tools)} tools.")
    confirm = input("Continue? (y/n): ")
    if confirm.lower() == 'y':
        install_tools(tools)
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()
