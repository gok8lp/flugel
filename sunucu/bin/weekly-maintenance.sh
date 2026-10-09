#!/bin/bash
. /usr/local/lib/sistem-bakim/whatsapp-kapat.sh  # sistem-bakim
PHONE="<TELEFON>"; APIKEY="<CALLMEBOT_APIKEY>"
LOG=$(mktemp)
{
  apt-get update -qq && apt-get -y -qq upgrade
  apt-get -y -qq autoremove
  docker image prune -af
  journalctl --vacuum-time=14d
  fstrim -av
} >> "$LOG" 2>&1
UPG=$(grep -c "^Unpacking\|^Setting up" "$LOG" || echo 0)
curl -s -G "https://api.callmebot.com/whatsapp.php" \
  --data-urlencode "phone=$PHONE" \
  --data-urlencode "text=🧰 Haftalik bakim tamam. Paket islemi: $UPG. Disk temizligi + trim yapildi." \
  --data-urlencode "apikey=$APIKEY" >/dev/null
rm -f "$LOG"
