#!/usr/bin/env bash

echo "💻 Installing Visual Studio Code..."
cd /tmp
wget -q "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64" -O code.deb || true
sudo dpkg -i code.deb || sudo apt-get install -f -y || true
rm -f code.deb || true
nohup code >/dev/null 2>&1 || true