#!/bin/bash
. /usr/local/lib/sistem-bakim/whatsapp-kapat.sh  # sistem-bakim
PHONE="<TELEFON>"
APIKEY="<CALLMEBOT_APIKEY>"
STATE_DIR="/var/lib/docker-monitor"
mkdir -p "$STATE_DIR"

send() {
  curl -s -G "https://api.callmebot.com/whatsapp.php" \
    --data-urlencode "phone=$PHONE" \
    --data-urlencode "text=$1" \
    --data-urlencode "apikey=$APIKEY" > /dev/null
  sleep 4
}

# Cikis kodu yorumlayici
explain_exit() {
  local code=$1
  case $code in
    0)   echo "Normal cikis" ;;
    1)   echo "Genel hata (app kodunda exception)" ;;
    125) echo "Docker daemon hatasi" ;;
    126) echo "Container komutu calistirilabilir degil" ;;
    127) echo "Container komutu bulunamadi" ;;
    130) echo "Ctrl+C ile durduruldu (SIGINT)" ;;
    137) echo "OOM-killed veya SIGKILL (bellek yetersiz)" ;;
    139) echo "Segmentation fault (uygulama cokmesi)" ;;
    143) echo "SIGTERM ile durduruldu" ;;
    *)   echo "Bilinmeyen exit kodu" ;;
  esac
}

# === 1. Yeni UNHEALTHY ===
CURR_UNHEALTHY=$(docker ps --filter health=unhealthy --format "{{.Names}}" | sort)
LAST_UNHEALTHY=$(cat "$STATE_DIR/unhealthy.last" 2>/dev/null || true)
for c in $CURR_UNHEALTHY; do
  if ! echo "$LAST_UNHEALTHY" | grep -qx "$c"; then
    IMAGE=$(docker inspect --format='{{.Config.Image}}' "$c" 2>/dev/null)
    HC_LOG=$(docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' "$c" 2>/dev/null | tail -c 300)
    LOGS=$(docker logs --tail 8 "$c" 2>&1 | tail -8)
    send "🚨 DOCKER UNHEALTHY

📦 Container: $c
🖼️ Image: $IMAGE

❤️ Healthcheck cikti:
$HC_LOG

📋 Son loglar:
$LOGS"
  fi
done
echo "$CURR_UNHEALTHY" > "$STATE_DIR/unhealthy.last"

# === 2. Yeni EXIT (kod != 0) ===
CURR_EXITED=$(docker ps -a --filter "status=exited" --format "{{.Names}}" | sort)
LAST_EXITED=$(cat "$STATE_DIR/exited.last" 2>/dev/null || true)

while IFS= read -r c; do
  [ -z "$c" ] && continue
  # GPU sanal makineye verilirken libvirt hook'unun bilerek durdurdugu konteynerler: alarm yok (sistem-bakim)
  grep -qx "$c" /run/gpu-hook-durdurulan 2>/dev/null && continue
  if ! echo "$LAST_EXITED" | grep -qx "$c"; then
    EXIT_CODE=$(docker inspect --format='{{.State.ExitCode}}' "$c" 2>/dev/null)
    [ "$EXIT_CODE" = "0" ] && continue  # normal cikis, sessiz gec

    STATUS=$(docker ps -a --filter "name=^${c}$" --format "{{.Status}}")
    IMAGE=$(docker inspect --format='{{.Config.Image}}' "$c" 2>/dev/null)
    OOM=$(docker inspect --format='{{.State.OOMKilled}}' "$c" 2>/dev/null)
    ERR=$(docker inspect --format='{{.State.Error}}' "$c" 2>/dev/null)
    STARTED=$(docker inspect --format='{{.State.StartedAt}}' "$c" 2>/dev/null | cut -d. -f1)
    FINISHED=$(docker inspect --format='{{.State.FinishedAt}}' "$c" 2>/dev/null | cut -d. -f1)
    REASON=$(explain_exit "$EXIT_CODE")
    LOGS=$(docker logs --tail 10 "$c" 2>&1 | tail -10)

    EXTRA=""
    [ "$OOM" = "true" ] && EXTRA="$EXTRA
💀 OOM-killed: Bellek yetersizdi!"
    [ -n "$ERR" ] && EXTRA="$EXTRA
⚠️ Hata: $ERR"

    send "💥 DOCKER PATLADI

📦 Container: $c
🖼️ Image: $IMAGE
📊 Status: $STATUS
🔢 Exit code: $EXIT_CODE
💬 Sebep: $REASON$EXTRA

🕐 Basladi: $STARTED
🕐 Durdu: $FINISHED

📋 Son loglar:
$LOGS"
  fi
done <<< "$CURR_EXITED"
echo "$CURR_EXITED" > "$STATE_DIR/exited.last"

# === 3. Restart loop ===
for c in $(docker ps --filter "status=running" --format "{{.Names}}"); do
  RC=$(docker inspect --format='{{.RestartCount}}' "$c" 2>/dev/null)
  [ -z "$RC" ] && continue
  LAST_RC=$(cat "$STATE_DIR/rc-$c" 2>/dev/null || echo 0)
  DELTA=$((RC - LAST_RC))
  if [ "$DELTA" -ge 3 ]; then
    IMAGE=$(docker inspect --format='{{.Config.Image}}' "$c")
    LOGS=$(docker logs --tail 10 "$c" 2>&1 | tail -10)
    send "🔄 DOCKER RESTART LOOP

📦 Container: $c
🖼️ Image: $IMAGE
🔁 Son kontrolden beri $DELTA kez restart oldu
🔢 Toplam restart: $RC

📋 Son loglar:
$LOGS"
  fi
  echo "$RC" > "$STATE_DIR/rc-$c"
done
