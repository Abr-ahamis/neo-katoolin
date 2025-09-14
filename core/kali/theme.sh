#!/usr/bin/env bash
set -euo pipefail

# Helper: Safely remove any existing file or directory
safe_rm() {
    if [ -e "$1" ]; then
        echo "⚠️ Removing existing: $1"
        sudo rm -rf "$1"
    fi
}

echo "=== Startup Script Beginning ==="

# 1️⃣ Resolve real user and environment
REAL_USER=$(logname)
USER_ID=$(id -u "$REAL_USER")
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$USER_ID/bus"
export XDG_RUNTIME_DIR="/run/user/$USER_ID"

# Helper: Run gsettings as the real user
gset() {
    sudo -u "$REAL_USER" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" gsettings "$@"
}

# 2️⃣ Clone/refresh 'startup' repo
safe_rm startup
echo "Cloning repository..."
git clone https://github.com/Abr-ahamis/startup.git || echo "⚠️ git clone failed, proceeding."

cd startup || { echo "❌ Cannot cd into 'startup'"; exit 1; }

# 3️⃣ Apply GRUB themes
safe_rm /boot/grub/themes/kali
sudo cp -r kali /boot/grub/themes || echo "⚠️ grub theme copy failed."

safe_rm /usr/share/grub/themes/kali
sudo cp -r /boot/grub/themes/kali /usr/share/grub/themes || echo "⚠️ grub theme copy failed."

# 4️⃣ Apply wallpapers
cd wallpaper || { echo "⚠️ Cannot cd into wallpaper folder."; exit 1; }

for img in kali-maze-16x9.jpg kali-tiles-16x9.jpg kali-oleo-16x9.png kali-tiles-purple-16x9.jpg kali-waves-16x9.png login.svg login-blurred; do
    sudo mv "/usr/share/backgrounds/kali/$img" "/usr/share/backgrounds/kali/${img}.b" 2>/dev/null || true
done

# Copy new wallpapers
sudo cp 20-wallpaper.svg /usr/share/backgrounds/kali/login.svg || true
sudo cp 12-wallpaper.png /usr/share/backgrounds/kali/kali-maze-16x9.jpg || true
sudo cp 1-wallpaper.png /usr/share/backgrounds/kali/kali-tiles-16x9.jpg || true
sudo cp 2-wallpaper.png /usr/share/backgrounds/kali/kali-waves-16x9.png || true
sudo cp 3-wallpaper.png /usr/share/backgrounds/kali/kali-oleo-16x9.png || true
sudo cp 4-wallpaper.png /usr/share/backgrounds/kali/kali-tiles-purple-16x9.jpg || true
sudo cp 2-wallpaper.png /usr/share/backgrounds/kali/login-blurred || true

# 5️⃣ GNOME Settings: Sleep, Interface, Dash-to-Dock
echo "⏰ Setting 2-hour sleep timer (AC)..."
gset set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 7200 || true
gset set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'suspend' || true

echo "💠 Applying GNOME interface settings..."
gset set org.gnome.desktop.interface font-name 'DejaVu Serif Condensed 10' || true
gset set org.gnome.desktop.interface text-scaling-factor 0.95 || true
gset set org.gnome.desktop.background picture-options 'zoom' || true

echo "🅾 Configuring Dash-to-Dock..."
gset set org.gnome.shell.extensions.dash-to-dock dock-position 'LEFT' || true
gset set org.gnome.shell.extensions.dash-to-dock autohide true || true
gset set org.gnome.shell.extensions.dash-to-dock animation-time 0.0 || true
gset set org.gnome.shell.extensions.dash-to-dock hide-delay 0.0 || true
gset set org.gnome.shell.extensions.dash-to-dock pressure-threshold 0.0 || true
gset set org.gnome.shell.extensions.dash-to-dock dash-max-icon-size 20 || true

echo "=== Startup Script Completed ==="
