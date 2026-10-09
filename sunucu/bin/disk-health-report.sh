#!/bin/bash
. /usr/local/lib/sistem-bakim/whatsapp-kapat.sh  # sistem-bakim
# Disk sağlık raporu — CallMeBot WhatsApp (akıllandırılmış sürüm)
[ -f /usr/local/bin/secrets.env ] && source /usr/local/bin/secrets.env
PHONE="${PHONE:-<TELEFON>}"
APIKEY="${APIKEY:-<CALLMEBOT_APIKEY>}"

STATE_DIR="/var/lib/disk-monitor"
mkdir -p "$STATE_DIR"
NOW=$(date +%s)
REPORT=""
HAS_WARNING=0

for DISK in sda sdb sdc sde; do
  [ ! -b "/dev/$DISK" ] && continue

  SMART=$(sudo smartctl -d sat -A "/dev/$DISK" 2>/dev/null)
  HEALTH=$(sudo smartctl -d sat -H "/dev/$DISK" 2>/dev/null | grep -i "overall-health" | awk -F: '{print $2}' | xargs)
  LCC=$(echo "$SMART" | awk '/Load_Cycle_Count/ {print $NF}')
  POH=$(echo "$SMART" | awk '/Power_On_Hours/ {print $NF}')
  TEMP=$(echo "$SMART" | awk '/Temperature_Celsius/ {print $10}' | head -1)
  PENDING=$(echo "$SMART" | awk '/Current_Pending_Sector/ {print $NF}')
  REALLOC=$(echo "$SMART" | awk '/Reallocated_Sector_Ct/ {print $NF}')

  LAST_FILE="$STATE_DIR/$DISK.last"
  TS_FILE="$STATE_DIR/$DISK.ts"
  DELTA="?"
  RATE="?"
  if [ -n "$LCC" ] && [ -f "$LAST_FILE" ]; then
    LAST_LCC=$(cat "$LAST_FILE" 2>/dev/null)
    if [ -n "$LAST_LCC" ] && [[ "$LAST_LCC" =~ ^[0-9]+$ ]] && [[ "$LCC" =~ ^[0-9]+$ ]]; then
      DELTA=$((LCC - LAST_LCC))
      if [ -f "$TS_FILE" ]; then
        LAST_TS=$(cat "$TS_FILE" 2>/dev/null)
        ELAPSED_H=$(( (NOW - LAST_TS) / 3600 ))
        [ "$ELAPSED_H" -lt 1 ] && ELAPSED_H=1
        RATE=$(( DELTA / ELAPSED_H ))
      fi
    fi
  fi

  if [ -n "$LCC" ] && [[ "$LCC" =~ ^[0-9]+$ ]]; then
    echo "$LCC" > "$LAST_FILE"
    echo "$NOW" > "$TS_FILE"
  fi

  WARN=""
  [ -n "$HEALTH" ] && [ "$HEALTH" != "PASSED" ] && WARN="$WARN [SMART_FAIL]" && HAS_WARNING=1
  [ "${PENDING:-0}" -gt 0 ] 2>/dev/null && WARN="$WARN [PENDING=$PENDING]" && HAS_WARNING=1
  [ "${REALLOC:-0}" -gt 0 ] 2>/dev/null && WARN="$WARN [REALLOC=$REALLOC]" && HAS_WARNING=1
  [ "${TEMP:-0}" -gt 50 ] 2>/dev/null && WARN="$WARN [TEMP=${TEMP}C]" && HAS_WARNING=1
  [ "$RATE" != "?" ] && [ "$RATE" -gt 25 ] 2>/dev/null && WARN="$WARN [PARK_HIZ=${RATE}/saat]" && HAS_WARNING=1

  if [ -z "$LCC" ]; then
    PARK_LINE="  Park: SSD (park yok)"
  else
    if [ "$RATE" != "?" ]; then
      PARK_LINE="  Park: ${LCC} (+${DELTA} / ~${RATE} saatte)"
    else
      PARK_LINE="  Park: ${LCC} (+${DELTA})"
    fi
  fi

  REPORT="$REPORT
/dev/$DISK
  Saglik: ${HEALTH:-?}
  Sicaklik: ${TEMP:-?}C
  Calisma: ${POH:-?} saat
$PARK_LINE
  Pending: ${PENDING:-0} | Realloc: ${REALLOC:-0}${WARN:+
  UYARI:$WARN}"
done

TITLE="Disk Saglik Raporu"
[ "$HAS_WARNING" = "1" ] && TITLE="!! DISK UYARISI !!"
MESSAGE="$TITLE
$REPORT"

curl -s -G "https://api.callmebot.com/whatsapp.php" \
  --data-urlencode "phone=$PHONE" \
  --data-urlencode "text=$MESSAGE" \
  --data-urlencode "apikey=$APIKEY" > /dev/null
