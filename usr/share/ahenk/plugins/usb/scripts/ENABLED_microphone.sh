#!/bin/bash
set -e

if [[ $EUID -ne 0 ]]; then
  echo "Bu script root olarak çalıştırılmalı."
  exit 1
fi

WP_CONF="/etc/wireplumber/wireplumber.conf.d/90-disable-microphones.conf"

restart_user_audio_stack() {
  local uid="$1"
  local user="$2"

  [[ -d "/run/user/$uid" ]] || return 0

  # WirePlumber servisini yeniden başlatarak silinen kuralın boşa çıkmasını sağlıyoruz
  sudo -u "$user" env \
    XDG_RUNTIME_DIR="/run/user/$uid" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$uid/bus" \
    systemctl --user restart wireplumber 2>/dev/null || true

  # Mikrofonların sesini tekrar aç (Susturmayı kaldır ve sesi %100 yap)
  sudo -u "$user" env \
    XDG_RUNTIME_DIR="/run/user/$uid" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$uid/bus" \
    bash -lc '
      if command -v pactl >/dev/null 2>&1; then
        pactl list short sources 2>/dev/null | grep -v "monitor" | awk "{print \$2}" | while read -r src; do
          [ -n "$src" ] && {
            pactl set-source-mute "$src" 0 2>/dev/null || true
            pactl set-source-volume "$src" 100% 2>/dev/null || true
          }
        done
      fi
    ' || true
}

if [[ -f "$WP_CONF" ]]; then
  rm -f "$WP_CONF"

  if command -v loginctl >/dev/null 2>&1; then
    while read -r uid user _; do
      [[ -n "${uid:-}" && -n "${user:-}" ]] || continue
      restart_user_audio_stack "$uid" "$user"
    done < <(loginctl list-users --no-legend 2>/dev/null || true)
  fi

  echo "İşlem tamamlandı. Mikrofonlar yeniden aktif."
else
  echo "Engelleme dosyası bulunamadı, sistem zaten orijinal durumunda."
fi