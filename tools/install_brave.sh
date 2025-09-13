#!/usr/bin/env bash

echo "🦁 Installing Brave Nightly..."
{
    curl -fsS https://dl.brave.com/install.sh | CHANNEL=nightly bash
} || echo "⚠️ Brave setup script failed."

# Pin Brave if available
for entry in brave-browser.desktop brave-browser-nightly.desktop brave.desktop; do
    if [ -f "/usr/share/applications/$entry" ]; then
        desktop="$entry"
        break
    fi
done
if [ -n "${desktop:-}" ]; then
    favs=$(gset get org.gnome.shell favorite-apps) || favs=""
    if [[ $favs != *"$desktop"* ]]; then
        new=$(echo "$favs" | sed "s/]$/, '$desktop']/") || new="$favs"
        gset set org.gnome.shell favorite-apps "$new" || true
    fi
fi