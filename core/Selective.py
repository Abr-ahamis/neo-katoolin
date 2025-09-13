#!/usr/bin/env python3
import subprocess
import sys
import os

def get_tools_by_category():
    categories = {}
    current_category = None
    
    try:
        with open('tools/list-tools.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Check if it's a category line (starts with #)
                if line.startswith('#'):
                    current_category = line[1:].strip()
                    categories[current_category] = []
                elif current_category and not line.startswith('#'):
                    categories[current_category].append(line)
    except FileNotFoundError:
        print("Error: tools/list-tools.txt not found.")
        return {}
    except Exception as e:
        print(f"Error reading tools list: {e}")
        return {}
    
    return categories

def display_categories(categories):
    print("\nAvailable Categories:")
    print("="*50)
    
    for i, category in enumerate(categories.keys(), 1):
        print(f"{i}) {category} ({len(categories[category])} tools)")
    
    return list(categories.keys())

def display_tools(category, tools):
    print(f"\nTools in {category}:")
    print("="*50)
    
    for i, tool in enumerate(tools, 1):
        print(f"{i}) {tool}")
    
    return tools

def install_tools(tools):
    success_count = 0
    fail_count = 0
    failed_tools = []
    
    for tool in tools:
        try:
            print(f"Installing {tool}...")
            subprocess.run(['apt-get', 'install', '-y', tool], check=True)
            print(f"{tool} installed successfully!")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"Error installing {tool}: {e}")
            fail_count += 1
            failed_tools.append(tool)
        except Exception as e:
            print(f"Unexpected error installing {tool}: {e}")
            fail_count += 1
            failed_tools.append(tool)
    
    print("\nInstallation Summary:")
    print(f"Successfully installed: {success_count} tools")
    print(f"Failed to install: {fail_count} tools")
    
    if failed_tools:
        print("\nFailed tools:")
        for tool in failed_tools:
            print(f"- {tool}")
    
    return success_count, fail_count

def main():
    print("\n" + "="*50)
    print("Selective Installation")
    print("="*50)
    
    if os.geteuid() != 0:
        print("This script requires root privileges. Please run with sudo.")
        return
    
    categories = get_tools_by_category()
    
    if not categories:
        print("No categories found. Exiting.")
        return
    
    category_names = display_categories(categories)
    
    while True:
        print("\nOptions:")
        print("Enter the number of the category you want to explore")
        print("Enter '0' to go back to the main menu")
        
        choice = input("\nEnter your choice: ")
        
        if choice == '0':
            print("Returning to main menu...")
            return
        
        try:
            category_index = int(choice) - 1
            if 0 <= category_index < len(category_names):
                selected_category = category_names[category_index]
                tools = categories[selected_category]
                
                while True:
                    display_tools(selected_category, tools)
                    
                    print("\nOptions:")
                    print("Enter the number of the tool you want to install")
                    print("Enter multiple numbers separated by commas (e.g., 1,3,5)")
                    print("Enter 'all' to install all tools in this category")
                    print("Enter '0' to go back to category selection")
                    
                    tool_choice = input("\nEnter your choice: ")
                    
                    if tool_choice == '0':
                        break
                    elif tool_choice.lower() == 'all':
                        confirm = input(f"Are you sure you want to install all {len(tools)} tools in {selected_category}? (y/n): ")
                        if confirm.lower() == 'y':
                            install_tools(tools)
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
                            confirm = input("Continue with installation? (y/n): ")
                            
                            if confirm.lower() == 'y':
                                install_tools(selected_tools)
                            else:
                                print("Operation cancelled.")
                        except (ValueError, IndexError):
                            print("Invalid input. Please enter valid numbers separated by commas.")
            else:
                print("Invalid category number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

if __name__ == "__main__":
    main()