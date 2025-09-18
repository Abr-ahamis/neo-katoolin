#!/bin/bash

set -euo pipefail

# === Colors ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo -e "${CYAN}🔍 Checking for system requirements and existing installation...${RESET}"

# === Variables ===
GPG_KEY_URL="https://www.virtualbox.org/download/oracle_vbox_2016.asc"
GPG_KEY_TMP="/tmp/oracle_vbox_2016.asc"
GPG_KEY_PATH="/usr/share/keyrings/vbox-archive-keyring.gpg"
REPO_FILE="/etc/apt/sources.list.d/virtualbox.list"
PACKAGE_NAME="virtualbox-7.0"
DISTRO_CODENAME="$(lsb_release -cs)"

# === Update System ===
echo -e "${CYAN}🔄 Updating system packages...${RESET}"
sudo apt update && sudo apt full-upgrade -y

# === Install Dependencies ===
echo -e "${CYAN}🔧 Installing required packages...${RESET}"
sudo apt install -y build-essential dkms linux-headers-$(uname -r) curl wget gnupg lsb-release

# === Handle GPG Key ===
if [[ -f "$GPG_KEY_PATH" ]]; then
    echo -e "${GREEN}✅ GPG key already exists at $GPG_KEY_PATH${RESET}"
    read -rp "❓ Do you want to replace the existing GPG key? (y/n): " replace_gpg
    if [[ "$replace_gpg" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🔑 Replacing GPG key...${RESET}"
        wget -q "$GPG_KEY_URL" -O "$GPG_KEY_TMP"
        sudo gpg --dearmor < "$GPG_KEY_TMP" | sudo tee "$GPG_KEY_PATH" > /dev/null
        rm -f "$GPG_KEY_TMP"
        echo -e "${GREEN}✅ GPG key updated.${RESET}"
    else
        echo -e "${YELLOW}⏩ Skipping GPG key import.${RESET}"
    fi
else
    echo -e "${YELLOW}🔑 GPG key not found. Importing...${RESET}"
    wget -q "$GPG_KEY_URL" -O "$GPG_KEY_TMP"
    sudo gpg --dearmor < "$GPG_KEY_TMP" | sudo tee "$GPG_KEY_PATH" > /dev/null
    rm -f "$GPG_KEY_TMP"
    echo -e "${GREEN}✅ GPG key imported.${RESET}"
fi

# === Handle Repository ===
if [[ -f "$REPO_FILE" ]]; then
    echo -e "${GREEN}✅ VirtualBox repo already exists at $REPO_FILE${RESET}"
    read -rp "❓ Do you want to replace the existing repo file? (y/n): " replace_repo
    if [[ "$replace_repo" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}📝 Replacing VirtualBox APT repo...${RESET}"
        echo "deb [signed-by=$GPG_KEY_PATH] https://download.virtualbox.org/virtualbox/debian $DISTRO_CODENAME contrib" | sudo tee "$REPO_FILE" > /dev/null
    else
        echo -e "${YELLOW}⏩ Skipping APT repo setup.${RESET}"
    fi
else
    echo -e "${YELLOW}➕ Adding VirtualBox APT repository...${RESET}"
    echo "deb [signed-by=$GPG_KEY_PATH] https://download.virtualbox.org/virtualbox/debian $DISTRO_CODENAME contrib" | sudo tee "$REPO_FILE" > /dev/null
fi

# === Update APT Cache ===
echo -e "${CYAN}🔄 Updating APT cache...${RESET}"
sudo apt update

# === Check If Installed ===
if dpkg -l | grep -q "$PACKAGE_NAME"; then
    echo -e "${GREEN}✅ VirtualBox 7.0 is already installed.${RESET}"
    read -rp "❓ Do you want to reinstall VirtualBox 7.0? (y/n): " reinstall_vbox
    if [[ "$reinstall_vbox" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🔁 Reinstalling VirtualBox...${RESET}"
        sudo apt install --reinstall -y "$PACKAGE_NAME"
    else
        echo -e "${YELLOW}⏩ Skipping VirtualBox installation.${RESET}"
    fi
else
    echo -e "${CYAN}📦 Installing VirtualBox 7.0...${RESET}"
    sudo apt install -y "$PACKAGE_NAME"
fi

# === Kernel Setup ===
if [[ -x /sbin/vboxconfig ]]; then
    echo -e "${CYAN}⚙️ Running vboxconfig...${RESET}"
    sudo /sbin/vboxconfig
elif [[ -x /usr/lib/virtualbox/vboxdrv.sh ]]; then
    echo -e "${CYAN}⚙️ Running vboxdrv.sh setup...${RESET}"
    sudo /usr/lib/virtualbox/vboxdrv.sh setup
else
    echo -e "${RED}⚠️ No VBox config tool found — kernel modules might not be loaded.${RESET}"
fi

# === Add user to vboxusers group ===
if groups "$USER" | grep -qw "vboxusers"; then
    echo -e "${GREEN}👤 User '$USER' is already in the vboxusers group.${RESET}"
else
    echo -e "${CYAN}➕ Adding user '$USER' to vboxusers group...${RESET}"
    sudo usermod -aG vboxusers "$USER"
    echo -e "${GREEN}✅ User added. You may need to logout/login for group changes to take effect.${RESET}"
fi

# === Load Kernel Module ===
if lsmod | grep -q vboxdrv; then
    echo -e "${GREEN}✅ vboxdrv kernel module is loaded.${RESET}"
else
    echo -e "${YELLOW}📦 Loading vboxdrv kernel module...${RESET}"
    if sudo modprobe vboxdrv; then
        echo -e "${GREEN}✅ vboxdrv loaded successfully.${RESET}"
    else
        echo -e "${RED}⚠️ Failed to load vboxdrv. Secure Boot may be interfering.${RESET}"
    fi
fi

# === Finish ===
echo ""
echo -e "${GREEN}✅ Installation and setup complete!${RESET}"
echo -e "${CYAN}🔁 Please reboot your system.${RESET}"
echo -e "${CYAN}🖥️ You can launch VirtualBox using the 'virtualbox' command or from your application menu.${RESET}"
