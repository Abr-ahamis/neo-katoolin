#!/usr/bin/env bash

echo "🔐 Installing ProtonVPN..."
wget -q https://repo.protonvpn.com/debian/dists/stable/main/binary-all/protonvpn-stable-release_1.0.8_all.deb -O /tmp/protonvpn.deb
sudo dpkg -i /tmp/protonvpn.deb 
sudo apt update
sudo apt install -y proton-vpn-gnome-desktop libayatana-appindicator3-1 gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator
nohup protonvpn-app >/dev/null 2>&1 