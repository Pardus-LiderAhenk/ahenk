#!/bin/bash
set -e

if [[ $EUID -ne 0 ]]; then
  echo "Bu script root olarak çalıştırılmalı."
  exit 1
fi

WP_DIR="/etc/wireplumber/wireplumber.conf.d"
WP_CONF="$WP_DIR/90-disable-microphones.conf"

restart_user_audio_stack() {
  local uid="$1"
  local user="$2"

  [[ -d "/run/user/$uid" ]] || return 0

  echo "Kullanıcı oturum servisleri yeniden başlatılıyor: $user ($uid)"

  sudo -u "$user" env \
    XDG_RUNTIME_DIR="/run/user/$uid" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$uid/bus" \
    systemctl --user restart wireplumber 2>/dev/null || true

  sudo -u "$user" env \
    XDG_RUNTIME_DIR="/run/user/$uid" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$uid/bus" \
    bash -lc '
      if command -v pactl >/dev/null 2>&1; then
        pactl list short sources 2>/dev/null | grep -v "monitor" | awk "{print \$2}" | while read -r src; do
          [ -n "$src" ] && {
            pactl set-source-mute "$src" 1 2>/dev/null || true
            pactl set-source-volume "$src" 0 2>/dev/null || true
          }
        done
      fi
    ' || true
}

DESIRED_CONF="$(cat <<'EOF'
monitor.alsa.rules = [
  {
    matches = [
      {
        media.class = "Audio/Source"
      }
    ]
    actions = {
      update-props = {
        node.passive = true
        audio.channels = 0
        node.disabled = true
      }
    }
  }
]

monitor.bluez.rules = [
  {
    matches = [
      {
        media.class = "Audio/Source"
      }
    ]
    actions = {
      update-props = {
        node.disabled = true
      }
    }
  }
]
EOF
)"

mkdir -p "$WP_DIR"

changed=0

if [[ -f "$WP_CONF" ]] && cmp -s "$WP_CONF" <(printf '%s\n' "$DESIRED_CONF"); then
  echo "Zaten uygulanmış: Konfigürasyon güncel."
else
  printf '%s\n' "$DESIRED_CONF" > "$WP_CONF"
  echo "Yeni güvenli konfigürasyon yazıldı: $WP_CONF"
  changed=1
fi

if [[ "$changed" -eq 1 ]]; then
  if command -v loginctl >/dev/null 2>&1; then
    while read -r uid user _; do
      [[ -n "${uid:-}" && -n "${user:-}" ]] || continue
      restart_user_audio_stack "$uid" "$user"
    done < <(loginctl list-users --no-legend 2>/dev/null || true)
  fi

  echo "İşlem tamamlandı."
else
  echo "Değişiklik yok, işlem atlandı."
fi