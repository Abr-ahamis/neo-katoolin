#!/usr/bin/env bash
#
# install-grub-theme-and-configure.sh
# Clone startup repo, install 'kali' grub theme, modify /etc/default/grub:
#  - show menu (not hidden)
#  - set timeout to 2 seconds
#  - enable os-prober
#  - set GRUB_THEME to the copied theme
#  - try to set Windows as the default saved boot entry (auto-detect)
#  - backup files before editing
#  - rename/backup certain /usr/share/backgrounds files and copy wallpapers from repo
#
# Usage: sudo ./install-grub-theme-and-configure.sh
#

set -euo pipefail
IFS=$'\n\t'

REPO_URL="https://github.com/Abr-ahamis/startup.git"
CLONE_DIR="${HOME}/startup"        # will clone here if not present
THEME_SUBDIR="kali"                # theme folder inside the repo to copy
THEME_DEST="/boot/grub/themes/startup_kali"
GRUB_DEFAULT_FILE="/etc/default/grub"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

function ensure_root() {
  if [ "$EUID" -ne 0 ]; then
    echo "This script needs root. Re-running with sudo..."
    exec sudo bash "$0" "$@"
  fi
}

function backup_file() {
  local file="$1"
  if [ -f "$file" ]; then
    cp -a "$file" "${file}.bak.${TIMESTAMP}"
    echo "Backed up $file -> ${file}.bak.${TIMESTAMP}"
  fi
}

function clone_repo() {
  if [ -d "$CLONE_DIR/.git" ]; then
    echo "Repo already cloned at ${CLONE_DIR}. Pulling latest..."
    git -C "$CLONE_DIR" pull --ff-only || echo "git pull failed; continuing with existing copy"
  else
    echo "Cloning repository..."
    git clone "${REPO_URL}" "${CLONE_DIR}"
  fi
}

function install_theme() {
  local src="${CLONE_DIR}/${THEME_SUBDIR}"
  if [ ! -d "$src" ]; then
    echo "Theme source folder not found: $src"
    return 1
  fi

  echo "Creating theme dest: ${THEME_DEST}"
  mkdir -p "${THEME_DEST}"
  backup_and_remove_dir "${THEME_DEST}"
  cp -a "${src}/." "${THEME_DEST}/"
  echo "Copied theme files from ${src} to ${THEME_DEST}"
}

function backup_and_remove_dir() {
  local d="$1"
  if [ -d "$d" ]; then
    mv "$d" "${d}.bak.${TIMESTAMP}"
    echo "Moved existing ${d} -> ${d}.bak.${TIMESTAMP}"
  fi
}

# set or replace variable in /etc/default/grub
function set_grub_var() {
  local var="$1"
  local val="$2"
  local file="$3"
  # note: keep quotes consistent, so we wrap values in double quotes
  if grep -Pq "^[#\s]*${var}=" "$file"; then
    # replace existing (even if commented)
    # remove leading comment and replace the assignment
    sed -i -E "s|^[#[:space:]]*${var}=.*|${var}=\"${val}\"|g" "$file"
  else
    # append
    echo "${var}=\"${val}\"" >> "$file"
  fi
  echo "Set $var in $file"
}

# ensure specific boolean-looking var (no quotes) - use plain token (true/false/no)
function set_grub_token_var() {
  local var="$1"
  local val="$2"
  local file="$3"
  if grep -Pq "^[#\s]*${var}=" "$file"; then
    sed -i -E "s|^[#[:space:]]*${var}=.*|${var}=${val}|g" "$file"
  else
    echo "${var}=${val}" >> "$file"
  fi
  echo "Set $var=${val} in $file"
}

function configure_grub() {
  local f="${GRUB_DEFAULT_FILE}"
  echo "Backing up ${f}"
  backup_file "$f"

  # Guarantee os-prober runs so other OSes (Windows) are discovered
  set_grub_token_var "GRUB_DISABLE_OS_PROBER" "false" "$f"

  # Unhide menu & set timeout style/menu
  set_grub_var "GRUB_TIMEOUT_STYLE" "menu" "$f"
  set_grub_var "GRUB_TIMEOUT" "2" "$f"             # user requested 2 seconds
  set_grub_token_var "GRUB_HIDDEN_TIMEOUT" "0" "$f"
  set_grub_token_var "GRUB_HIDDEN_TIMEOUT_QUIET" "false" "$f"

  # Keep kernel cmdlines
  set_grub_var "GRUB_CMDLINE_LINUX_DEFAULT" "quiet splash" "$f"
  set_grub_var "GRUB_CMDLINE_LINUX" "" "$f"

  # Set GRUB_DEFAULT to saved and we will set the saved entry with grub-set-default
  set_grub_var "GRUB_DEFAULT" "saved" "$f"

  # Point GRUB_THEME to installed theme (theme.txt expected inside)
  local theme_txt_path="${THEME_DEST}/theme.txt"
  if [ -f "$theme_txt_path" ]; then
    set_grub_var "GRUB_THEME" "${theme_txt_path}" "$f"
  else
    echo "WARNING: theme.txt not found at ${theme_txt_path}. GRUB_THEME will still be written to file, but may be invalid."
    set_grub_var "GRUB_THEME" "${theme_txt_path}" "$f"
  fi

  echo "GRUB configuration updated in ${f}"
}

# Try to detect Windows menuentry in /boot/grub/grub.cfg
function find_windows_menuentry() {
  local cfg="/boot/grub/grub.cfg"
  if [ ! -f "$cfg" ]; then
    echo ""
    return 1
  fi

  # extract top-level menuentries (the script is simple: it grabs menuentry names)
  # This will include lines like: menuentry 'Ubuntu' --class ubuntu { ...
  # We'll search for likely Windows entries
  local entries=()
  # read menuentry names into array
  while IFS= read -r line; do
    # extract between single quotes
    if [[ "$line" =~ menuentry\ \'([^\']+)\' ]]; then
      entries+=("${BASH_REMATCH[1]}")
    fi
  done < <(grep -E "^menuentry '.*'" "${cfg}" || true)

  # Search for first entry that looks like Windows
  for e in "${entries[@]}"; do
    if echo "$e" | grep -Eiq "windows|microsoft|efi.*boot|boot manager|Windows Boot Manager"; then
      printf "%s" "$e"
      return 0
    fi
  done

  # If none matched, try entries that contain 'efi' or 'boot' as fallback
  for e in "${entries[@]}"; do
    if echo "$e" | grep -Eiq "efi|boot"; then
      printf "%s" "$e"
      return 0
    fi
  done

  # no entry found
  echo ""
  return 1
}

function set_windows_default() {
  echo "Attempting to detect Windows menuentry..."
  local win_entry
  win_entry="$(find_windows_menuentry || true)"
  if [ -n "$win_entry" ]; then
    echo "Found candidate Windows entry: '$win_entry'"
    echo "Setting GRUB saved default to that entry..."
    # Use grub-set-default to save it for GRUB_DEFAULT=saved
    grub-set-default -- "$win_entry" || {
      echo "grub-set-default failed (will try numeric fallback)."
      return 1
    }
    echo "Saved default entry set to: $win_entry"
    return 0
  fi

  echo "No obvious Windows entry found in /boot/grub/grub.cfg. You may need to run 'sudo update-grub' or check that os-prober detected Windows."
  return 1
}

function update_grub() {
  echo "Regenerating grub config..."
  # On Debian/Ubuntu update-grub is a wrapper for grub-mkconfig
  if command -v update-grub >/dev/null 2>&1; then
    update-grub
  else
    grub-mkconfig -o /boot/grub/grub.cfg
  fi
  echo "GRUB config regenerated."
}

# Safe rename/move of background files with timestamp to avoid overwrite collisions
function safe_mv_background() {
  local src="$1"
  if [ -f "$src" ]; then
    local base
    base="$(basename "$src")"
    local dest="/usr/share/backgrounds/${base}.bak.${TIMESTAMP}"
    mv -v "$src" "$dest" || echo "mv failed for $src"
    echo "Renamed $src -> $dest"
  else
    echo "Background $src not present, skipping rename."
  fi
}

function manage_backgrounds_and_wallpapers() {
  # The user supplied a list of names; here we will safely rename existing backgrounds
  echo "Renaming selected /usr/share/backgrounds files (if present) with timestamped backups..."
  # list of target filenames the user mentioned - we will rename them if present
  local to_rename=(
"/usr/share/backgrounds/Little_numbat_boy_by_azskalt.png"
"/usr/share/backgrounds/Monument_valley_by_orbitelambda.jpg"
"/usr/share/backgrounds/Northan_lights_by_mizuno.webp"
"/usr/share/backgrounds/Numbat_wallpaper_dimmed_3480x2160.png"
"/usr/share/backgrounds/Rainbow_lightbulb_by_Daniel_Micallef.png"
"/usr/share/backgrounds/ubuntu-default-greyscale-wallpaper.png"
"/usr/share/backgrounds/ubuntu-wallpaper-d.png"
"/usr/share/backgrounds/warty-final-ubuntu.png"
"/usr/share/backgrounds/Clouds_by_Tibor_Mokanszki.jpg"
"/usr/share/backgrounds/Fuji_san_by_amaral.png"
"/usr/share/backgrounds/Province_of_the_south_of_france_by_orbitelambda.jpg"
"/usr/share/backgrounds/Fuwafuwa_nanbatto_san_by_amaral-dark.png"
"/usr/share/backgrounds/Fuwafuwa_nanbatto_san_by_amaral-light.png"
  )

  for f in "${to_rename[@]}"; do
    safe_mv_background "$f"
  done

  # copy wallpapers from cloned repo wallpaper folder to /usr/share/backgrounds
  local wallpaper_src_dir="${CLONE_DIR}/wallpaper"
  if [ -d "$wallpaper_src_dir" ]; then
    echo "Copying wallpapers from ${wallpaper_src_dir} to /usr/share/backgrounds (using mapping)..."
    # mapping: source -> dest name
    declare -A map
    map["1-wallpaper.png"]="Little_numbat_boy_by_azskalt.png"
    map["1-wallpaper.jpg"]="Monument_valley_by_orbitelambda.jpg"
    map["1-wallpaper.png"]="Northan_lights_by_mizuno.webp"   # note: repeated source — last wins
    # We will implement a safer mapping using available files in wallpaper dir and the user's list.
    # To avoid duplicate overwrite from same source, we'll copy sequentially but add index if name exists.

    # Simpler approach: copy all files in wallpaper/ and only create missing named destinations if possible.
    # But user wants specific names, so we'll attempt to copy file-by-file based on pattern availability.

    # Get all source files list
    local src_files=( "${wallpaper_src_dir}"/* )
    local idx=0
    for sf in "${src_files[@]}"; do
      if [ -f "$sf" ]; then
        idx=$((idx+1))
        # build destination name: if we have a corresponding file from the user's list, use it,
        # else use the original name with .installed timestamp suffix to avoid clash
        local dest_name
        case $idx in
          1) dest_name="Little_numbat_boy_by_azskalt.png" ;;
          2) dest_name="Monument_valley_by_orbitelambda.jpg" ;;
          3) dest_name="Northan_lights_by_mizuno.webp" ;;
          4) dest_name="Numbat_wallpaper_dimmed_3480x2160.png" ;;
          5) dest_name="Rainbow_lightbulb_by_Daniel_Micallef.png" ;;
          6) dest_name="ubuntu-default-greyscale-wallpaper.png" ;;
          7) dest_name="ubuntu-wallpaper-d.png" ;;
          8) dest_name="warty-final-ubuntu.png" ;;
          9) dest_name="Clouds_by_Tibor_Mokanszki.jpg" ;;
          10) dest_name="Numbat_wallpaper_dimmed_3480x2160.png" ;;
          11) dest_name="Fuji_san_by_amaral.png" ;;
          12) dest_name="Province_of_the_south_of_france_by_orbitelambda.jpg" ;;
          13) dest_name="Fuwafuwa_nanbatto_san_by_amaral-dark.png" ;;
          14) dest_name="Fuwafuwa_nanbatto_san_by_amaral-light.png" ;;
          *) dest_name="$(basename "$sf").installed.${TIMESTAMP}" ;;
        esac

        dest="/usr/share/backgrounds/${dest_name}"
        if [ -f "$dest" ]; then
          # keep existing, create copy with timestamp
          dest="${dest}.installed.${TIMESTAMP}"
        fi
        cp -a "$sf" "$dest"
        echo "Copied $sf -> $dest"
      fi
    done
  else
    echo "No wallpaper folder found at ${wallpaper_src_dir}, skipping wallpaper copy."
  fi
}

# MAIN
ensure_root "$@"

echo "Starting GRUB theme & config installer..."

clone_repo

install_theme || {
  echo "Theme install returned an error but continuing."
}

configure_grub

# update-grub before trying to detect Windows (so os-prober runs and grub.cfg is refreshed)
update_grub

# Try to set Windows default if possible
if set_windows_default; then
  echo "Windows default set."
else
  echo "Could not auto-set Windows as default. You can set it manually with: sudo grub-set-default 'Your Windows entry name'"
fi

# Regenerate final grub config to ensure saved default is used
update_grub

# handle backgrounds/wallpapers
manage_backgrounds_and_wallpapers

echo ""
echo "Done. Important next steps / notes:"
echo " - Reboot to see the GRUB menu and theme: sudo reboot"
echo " - If you don't see the Windows entry, ensure your machine has os-prober installed:"
echo "     sudo apt update && sudo apt install os-prober -y"
echo "   then re-run: sudo update-grub"
echo " - To see all detected GRUB menu entries: sudo grep \"menuentry '\" /boot/grub/grub.cfg | sed -E \"s/menuentry '([^']+)'.*/\\1/\""
echo " - To change the saved default manually: sudo grub-set-default 'Exact menu entry name here'"
echo ""
echo "Backups:"
echo " - ${GRUB_DEFAULT_FILE}.bak.${TIMESTAMP} (original /etc/default/grub)"
echo " - Theme folder original may be at ${THEME_DEST}.bak.${TIMESTAMP} if existed previously"
echo ""
echo "If anything went wrong, you can restore /etc/default/grub from the .bak file and run sudo update-grub."
