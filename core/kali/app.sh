#!/usr/bin/env bash
# Install Brave (Nightly)
curl -fsS https://dl.brave.com/install.sh | CHANNEL=nightly sh
# Download latest Telegram tarball automatically
url=$(wget -qO- https://telegram.org/dl/desktop/linux | grep -oP 'https://telegram.org/dl/desktop/linux/tsetup\.\d+\.\d+\.\d+\.tar\.xz' | head -n 1)
echo "Downloading: $url"
wget -q "$url" -O tsetup_latest.tar.xz
sudo rm -rf /bin/Telegram
sudo tar -xf tsetup_latest.tar.xz -C /bin
cd /bin/Telegram
sudo chmod +x Telegram
./Telegram &
# Install ProtonVPN
wget https://repo.protonvpn.com/debian/dists/stable/main/binary-all/protonvpn-stable-release_1.0.8_all.deb -O /tmp/protonvpn-release.deb
sudo dpkg -i /tmp/protonvpn-release.deb
sudo apt update
sudo apt install -y proton-vpn-gnome-desktop
sudo apt install -y libayatana-appindicator3-1 gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator
protonvpn-app &
# Install RustScan
wget https://github.com/RustScan/RustScan/releases/download/2.2.3/rustscan_2.2.3_amd64.deb
sudo dpkg -i rustscan_2.2.3_amd64.deb
sudo apt-get install -f  # Fix any missing dependencies
# Increase file descriptor limit
ulimit -n 5000
# Download the latest VS Code .deb package
wget -q "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64" -O code.deb
sudo dpkg -i code.deb || sudo apt-get install -f -y
rm -f code.deb
code &