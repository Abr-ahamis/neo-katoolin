#!/usr/bin/env python3
import subprocess
import sys
import os

def check_repo_exists():
    try:
        with open('/etc/apt/sources.list', 'r') as f:
            content = f.read()
            if 'kali' in content.lower():
                return True
        return False
    except Exception as e:
        print(f"Error checking repository: {e}")
        return False

def add_kali_repo():
    try:
        # Backup sources.list
        subprocess.run(['cp', '/etc/apt/sources.list', '/etc/apt/sources.list.bak'], check=True)
        
        # Add Kali Linux repository
        with open('/etc/apt/sources.list', 'a') as f:
            f.write('\n# Kali Linux repository\ndeb http://http.kali.org/kali kali-rolling main non-free contrib\n')
        
        # Download and add Kali Linux signing key
        subprocess.run(['wget', '-q', '-O', '-', 'https://archive.kali.org/archive-key.asc'], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
        subprocess.run(['apt-key', 'add', '-'], input=subprocess.PIPE, check=True)
        
        # Update package lists
        print("Updating package lists...")
        subprocess.run(['apt-get', 'update'], check=True)
        
        print("Kali Linux repository added successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error adding repository: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("Add Kali Linux Repository")
    print("="*50)
    
    if os.geteuid() != 0:
        print("This script requires root privileges. Please run with sudo.")
        return
    
    if check_repo_exists():
        print("Kali Linux repository already exists in your system.")
        choice = input("Do you want to re-add it? (y/n): ")
        if choice.lower() != 'y':
            print("Operation cancelled.")
            return
    
    print("This will add the Kali Linux repository to your system.")
    print("Make sure you understand the risks of adding third-party repositories.")
    
    confirm = input("Continue? (y/n): ")
    if confirm.lower() == 'y':
        if add_kali_repo():
            print("Repository added successfully!")
        else:
            print("Failed to add repository.")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()