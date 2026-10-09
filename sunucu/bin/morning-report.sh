#!/bin/bash
. /usr/local/lib/sistem-bakim/whatsapp-kapat.sh  # sistem-bakim
PHONE="<TELEFON>"
APIKEY="<CALLMEBOT_APIKEY>"

# === Rastgele mutlu mesaj ===
QUOTES=(
"Bugun harika bir gun olacak ☀️"
"Sen de sunucun gibi guclusun, devam 💪"
"Kahveni al, dunya seni bekliyor ☕"
"Bir gun her sey yerine oturacak. Belki bugun 🌱"
"Hayat kisa, kodunu temiz yaz 🧹"
"Bugun kendine iyi davran 🫶"
"Server calisiyor, sen de calismalisin 😄"
"Kucuk adimlar buyuk yolculuklar yapar 👣"
"Hayalini kurdugun sey bir komut uzakta 🚀"
"Bugun biraz mola ver, hak ettin 🌸"
"Iyi ki varsin, sunucun bile farkinda 🤖❤️"
"Gulumse, log dosyalari bile temiz bugun 😊"
"Her hata bir ders, her ban bir zafer 🛡️"
"Stresli misin? Bir bardak su ic, derin nefes al 💧"
"Sen muhtesem bir homelab kurmussun, gurur duy 🏆"
"Bugun bir seyleri yedeklemeyi unutma 💾"
"Disklerin donuyor, sen de donmeye devam et 🌀"
"Karanlikta calisiyorsan bile parliyorsun ✨"
"Bugun sen ol, baska kimse degil 🌟"
"Dunya boyle gidiyor, sen sakin ol 🧘"
)
QUOTE="${QUOTES[$RANDOM % ${#QUOTES[@]}]}"

# === Yuk ===
LOAD=$(uptime | awk -F'load average: ' '{print $2}' | awk -F, '{print $1}' | xargs)
CORES=$(nproc)
LOAD_INT=$(echo "$LOAD" | cut -d. -f1)
[ "$LOAD_INT" -lt "$CORES" ] && LOAD_I="✅" || LOAD_I="❌"

# === RAM ===
RAM_PCT=$(free | awk '/Mem:/ {printf "%.0f", $3/$2*100}')
RAM_USED=$(free -h | awk '/Mem:/ {print $3}')
RAM_TOT=$(free -h | awk '/Mem:/ {print $2}')
[ "$RAM_PCT" -lt 85 ] && RAM_I="✅" || RAM_I="❌"

# === Swap ===
SWAP_PCT=$(free | awk '/Swap:/ {if($2>0) printf "%.0f", $3/$2*100; else print 0}')
[ "$SWAP_PCT" -lt 50 ] && SWAP_I="✅" || SWAP_I="❌"

# === Disk doluluk ===
DISK_I="✅"
DISK_DETAIL=""
while read line; do
  pct=$(echo "$line" | awk '{print $5}' | tr -d '%')
  mnt=$(echo "$line" | awk '{print $6}')
  used=$(echo "$line" | awk '{print $3}')
  size=$(echo "$line" | awk '{print $2}')
  if [ "$pct" -gt 90 ]; then
    DISK_I="❌"
    DISK_DETAIL="$DISK_DETAIL
   ❌ $mnt: %$pct ($used/$size)"
  elif [ "$pct" -gt 80 ]; then
    DISK_DETAIL="$DISK_DETAIL
   ⚠️ $mnt: %$pct ($used/$size)"
  fi
done < <(df -h | grep "^/dev/")

# === CPU sicaklik ===
TEMP=$(sensors 2>/dev/null | awk '/Tctl/ {gsub(/[+°C]/,"",$2); print $2}' | cut -d. -f1)
[ -z "$TEMP" ] && TEMP_I="❓" || { [ "$TEMP" -lt 75 ] && TEMP_I="✅" || TEMP_I="❌"; }

# === SMART durumu (detayli) ===
SMART_I="✅"
SMART_DETAIL=""
for d in sda sdb sdc sde; do
  [ ! -b "/dev/$d" ] && continue
  h=$(sudo smartctl -d sat -H /dev/$d 2>/dev/null | awk -F: '/overall-health/ {print $2}' | xargs)
  pending=$(sudo smartctl -d sat -A /dev/$d 2>/dev/null | awk '/Current_Pending_Sector/ {print $NF}')
  realloc=$(sudo smartctl -d sat -A /dev/$d 2>/dev/null | awk '/Reallocated_Sector_Ct/ {print $NF}')
  dtemp=$(sudo smartctl -d sat -A /dev/$d 2>/dev/null | awk '/Temperature_Celsius/ {print $10}' | head -1)
  if [ "$h" != "PASSED" ] || [ "${pending:-0}" -gt 0 ] || [ "${realloc:-0}" -gt 0 ]; then
    SMART_I="❌"
    SMART_DETAIL="$SMART_DETAIL
   ❌ $d: health=$h pending=${pending:-0} realloc=${realloc:-0} ${dtemp:-?}C"
  fi
done

# === Docker durumu (detayli) ===
D_RUN=$(docker ps -q | wc -l)
D_TOT=$(docker ps -aq | wc -l)
D_UNHEALTHY_LIST=$(docker ps --filter health=unhealthy --format "{{.Names}}")
D_EXITED_LIST=$(docker ps -a --filter "status=exited" --filter "status=dead" --format "{{.Names}}|{{.Status}}" | grep -v "Exited (0)" || true)
D_DETAIL=""
D_I="✅"

if [ -n "$D_UNHEALTHY_LIST" ]; then
  D_I="❌"
  D_DETAIL="$D_DETAIL
   ❌ Unhealthy:"
  while IFS= read -r c; do
    [ -z "$c" ] && continue
    D_DETAIL="$D_DETAIL
      • $c"
  done <<< "$D_UNHEALTHY_LIST"
fi

if [ -n "$D_EXITED_LIST" ]; then
  D_I="❌"
  D_DETAIL="$D_DETAIL
   ❌ Patladi:"
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    name=$(echo "$line" | cut -d'|' -f1)
    status=$(echo "$line" | cut -d'|' -f2)
    D_DETAIL="$D_DETAIL
      • $name ($status)"
  done <<< "$D_EXITED_LIST"
fi

# === Failed systemd ===
FAILED_LIST=$(systemctl --failed --no-legend | awk '{print $2}')
FAILED=$(echo "$FAILED_LIST" | grep -c . || true)
SVC_DETAIL=""
if [ "$FAILED" -gt 0 ]; then
  SVC_I="❌"
  while IFS= read -r s; do
    [ -z "$s" ] && continue
    SVC_DETAIL="$SVC_DETAIL
   ❌ $s"
  done <<< "$FAILED_LIST"
else
  SVC_I="✅"
fi

# === Saldiri istatistikleri ===
BAN_TOTAL=$(sudo cscli decisions list -o raw 2>/dev/null | tail -n +2 | wc -l)
BAN_24H=$(sudo cscli alerts list --since 24h -o raw 2>/dev/null | tail -n +2 | wc -l)
F2B_BAN=$(sudo fail2ban-client status sshd 2>/dev/null | awk -F: '/Currently banned/ {print $2}' | xargs)

# === SSH son girisler ===
SSH_24H=$(sudo journalctl _COMM=sshd --since "24 hours ago" 2>/dev/null | grep -c "Accepted")
SSH_LAST=$(sudo journalctl _COMM=sshd --since "24 hours ago" 2>/dev/null | grep "Accepted" | tail -1 | awk '{print $1, $2, $3, "from", $(NF-3)}')

# === Uptime ===
UPTIME=$(uptime -p | sed 's/up //')

# === Mesaj ===
MESSAGE="🌅 Gunaydin!
$QUOTE

━━ SISTEM ━━
$LOAD_I Yuk: $LOAD / $CORES core
$RAM_I RAM: %$RAM_PCT ($RAM_USED/$RAM_TOT)
$SWAP_I Swap: %$SWAP_PCT
$TEMP_I CPU: ${TEMP:-?}C
⏱️ Uptime: $UPTIME

━━ DISK ━━
$DISK_I Doluluk${DISK_DETAIL:- ok}
$SMART_I SMART${SMART_DETAIL:- ok}

━━ DOCKER ━━
$D_I $D_RUN/$D_TOT container calisiyor${D_DETAIL:-}

━━ SERVISLER ━━
$SVC_I Failed: $FAILED${SVC_DETAIL:-}

━━ GUVENLIK ━━
🛡️ Son 24s saldiri: $BAN_24H
🚫 Aktif ban: $BAN_TOTAL
🔒 SSH f2b: ${F2B_BAN:-0}
🔑 SSH girisi (24s): $SSH_24H
${SSH_LAST:+   Son: $SSH_LAST}"

curl -s -G "https://api.callmebot.com/whatsapp.php" \
  --data-urlencode "phone=$PHONE" \
  --data-urlencode "text=$MESSAGE" \
  --data-urlencode "apikey=$APIKEY" > /dev/null
