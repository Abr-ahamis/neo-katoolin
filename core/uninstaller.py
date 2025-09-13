#!/usr/bin/env python3
import subprocess
import sys
import os

def get_installed_tools():
    try:
        # Get list of installed Kali tools
        result = subprocess.run(['dpkg', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        packages = result.stdout.split('\n')
        
        # Filter for Kali tools
        kali_tools = []
        for package in packages:
            if 'kali' in package.lower() and package.startswith('ii'):
                parts = package.split()
                if len(parts) >= 3:
                    kali_tools.append(parts[1])
        
        return kali_tools
    except Exception as e:
        print(f"Error getting installed tools: {e}")
        return []

def get_installed_apps():
    try:
        # Get list of installed apps
        result = subprocess.run(['dpkg', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        packages = result.stdout.split('\n')
        
        # Filter for specific apps
        apps = []
        for package in packages:
            if package.startswith('ii'):
                parts = package.split()
                if len(parts) >= 3:
                    package_name = parts[1]
                    if package_name in ['brave-browser', 'telegram-desktop', 'code']:
                        apps.append(package_name)
        
        return apps
    except Exception as e:
        print(f"Error getting installed apps: {e}")
        return []

def display_tools(tools):
    if not tools:
        print("No Kali Linux tools found installed.")
        return
    
    print("\nInstalled Kali Linux Tools:")
    print("="*50)
    
    # Calculate number of columns based on terminal width
    terminal_width = 80
    max_tool_length = max(len(tool) for tool in tools) if tools else 0
    columns = max(1, terminal_width // (max_tool_length + 4))
    
    for i in range(0, len(tools), columns):
        row = tools[i:i+columns]
        formatted_row = [f"{j+1}) {tool.ljust(max_tool_length)}" for j, tool in enumerate(row, start=i)]
        print("  ".join(formatted_row))
    
    return tools

def display_apps(apps):
    if not apps:
        print("No applications found installed.")
        return
    
    print("\nInstalled Applications:")
    print("="*50)
    
    for i, app in enumerate(apps, 1):
        print(f"{i}) {app}")
    
    return apps

def uninstall_tools(tools):
    success_count = 0
    fail_count = 0
    failed_tools = []
    
    for tool in tools:
        try:
            print(f"Uninstalling {tool}...")
            subprocess.run(['apt-get', 'remove', '--purge', '-y', tool], check=True)
            print(f"{tool} uninstalled successfully!")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling {tool}: {e}")
            fail_count += 1
            failed_tools.append(tool)
        except Exception as e:
            print(f"Unexpected error uninstalling {tool}: {e}")
            fail_count += 1
            failed_tools.append(tool)
    
    print("\nUninstallation Summary:")
    print(f"Successfully uninstalled: {success_count} tools")
    print(f"Failed to uninstall: {fail_count} tools")
    
    if failed_tools:
        print("\nFailed tools:")
        for tool in failed_tools:
            print(f"- {tool}")
    
    return success_count, fail_count

def uninstall_apps(apps):
    success_count = 0
    fail_count = 0
    failed_apps = []
    
    for app in apps:
        try:
            print(f"Uninstalling {app}...")
            subprocess.run(['apt-get', 'remove', '--purge', '-y', app], check=True)
            print(f"{app} uninstalled successfully!")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling {app}: {e}")
            fail_count += 1
            failed_apps.append(app)
        except Exception as e:
            print(f"Unexpected error uninstalling {app}: {e}")
            fail_count += 1
            failed_apps.append(app)
    
    print("\nUninstallation Summary:")
    print(f"Successfully uninstalled: {success_count} apps")
    print(f"Failed to uninstall: {fail_count} apps")
    
    if failed_apps:
        print("\nFailed apps:")
        for app in failed_apps:
            print(f"- {app}")
    
    return success_count, fail_count

def remove_kali_repo():
    try:
        print("Removing Kali Linux repository...")
        
        # Backup sources.list
        subprocess.run(['cp', '/etc/apt/sources.list', '/etc/apt/sources.list.bak'], check=True)
        
        # Read sources.list and remove Kali repo
        with open('/etc/apt/sources.list', 'r') as f:
            lines = f.readlines()
        
        with open('/etc/apt/sources.list', 'w') as f:
            for line in lines:
                if 'kali' not in line.lower():
                    f.write(line)
        
        # Update package lists
        subprocess.run(['apt-get', 'update'], check=True)
        
        print("Kali Linux repository removed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error removing Kali Linux repository: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error removing Kali Linux repository: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("Uninstall Kali Linux Tools and Applications")
    print("="*50)
    
    if os.geteuid() != 0:
        print("This script requires root privileges. Please run with sudo.")
        return
    
    while True:
        print("\nOptions:")
        print("1) Uninstall Kali Linux tools")
        print("2) Uninstall applications")
        print("3) Remove Kali Linux repository")
        print("0) Go back to main menu")
        
        choice = input("\nEnter your choice: ")
        
        if choice == '0':
            print("Returning to main menu...")
            return
        elif choice == '1':
            tools = get_installed_tools()
            display_tools(tools)
            
            if not tools:
                continue
                
            print("\nOptions:")
            print("Enter the number of the tool you want to uninstall")
            print("Enter multiple numbers separated by commas (e.g., 1,3,5)")
            print("Enter 'all' to uninstall all Kali Linux tools")
            print("Enter '0' to go back")
            
            tool_choice = input("\nEnter your choice: ")
            
            if tool_choice == '0':
                continue
            elif tool_choice.lower() == 'all':
                confirm = input(f"Are you sure you want to uninstall all {len(tools)} Kali Linux tools? (y/n): ")
                if confirm.lower() == 'y':
                    uninstall_tools(tools)
                else:
                    print("Operation cancelled.")
            else:
                try:
                    selected_indices = [int(x.strip()) - 1 for x in tool_choice.split(',')]
                    selected_tools = [tools[i] for i in selected_indices if 0 <= i < len(tools)]
                    
                    if not selected_tools:
                        print("Invalid selection. Please try again.")
                        continue
                    
                    print(f"\nSelected tools: {', '.join(selected_tools)}")
                    confirm = input("Continue with uninstallation? (y/n): ")
                    
                    if confirm.lower() == 'y':
                        uninstall_tools(selected_tools)
                    else:
                        print("Operation cancelled.")
                except (ValueError, IndexError):
                    print("Invalid input. Please enter valid numbers separated by commas.")
                    
        elif choice == '2':
            apps = get_installed_apps()
            display_apps(apps)
            
            if not apps:
                continue
                
            print("\nOptions:")
            print("Enter the number of the application you want to uninstall")
            print("Enter multiple numbers separated by commas (e.g., 1,3,5)")
            print("Enter 'all' to uninstall all applications")
            print("Enter '0' to go back")
            
            app_choice = input("\nEnter your choice: ")
            
            if app_choice == '0':
                continue
            elif app_choice.lower() == 'all':
                confirm = input(f"Are you sure you want to uninstall all {len(apps)} applications? (y/n): ")
                if confirm.lower() == 'y':
                    uninstall_apps(apps)
                else:
                    print("Operation cancelled.")
            else:
                try:
                    selected_indices = [int(x.strip()) - 1 for x in app_choice.split(',')]
                    selected_apps = [apps[i] for i in selected_indices if 0 <= i < len(apps)]
                    
                    if not selected_apps:
                        print("Invalid selection. Please try again.")
                        continue
                    
                    print(f"\nSelected applications: {', '.join(selected_apps)}")
                    confirm = input("Continue with uninstallation? (y/n): ")
                    
                    if confirm.lower() == 'y':
                        uninstall_apps(selected_apps)
                    else:
                        print("Operation cancelled.")
                except (ValueError, IndexError):
                    print("Invalid input. Please enter valid numbers separated by commas.")
                    
        elif choice == '3':
            confirm = input("Are you sure you want to remove the Kali Linux repository? (y/n): ")
            if confirm.lower() == 'y':
                remove_kali_repo()
            else:
                print("Operation cancelled.")
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()