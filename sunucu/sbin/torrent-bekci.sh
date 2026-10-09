#!/bin/bash
# Torrent bekcisi: Transmission'daki tum torrentlerin adini ve dosya listesini yasakli (CSAM) terimlere karsi tarar.
# Eslesme -> torrent + indirilen veri ANINDA silinir, kayit tutulur. (sistem-bakim)
YASAK='pthc|ptsc|hussyfan|r@ygold|raygold|babyshivid|kingpass|childlover|kinderporn|kiddy ?porn|pre-?teen|under-?age|jail-?bait|lolicon|\bloli\b|shotacon|\bshota\b|toddler|\b([4-9]|1[0-7]) ?yo\b|\b([4-9]|1[0-7]) ?(y\.?o\.?|years? old)\b|child ?(porn|sex|abuse)|pedo|paedo'
LOG=/var/log/torrent-bekci.log
TR="docker exec transmission transmission-remote"
ids=$($TR -l 2>/dev/null | awk 'NR>1 && $1 ~ /^[0-9]+\*?$/ {gsub(/\*/,"",$1); print $1}')
for id in $ids; do
  icerik=$($TR -t "$id" -i 2>/dev/null | grep -E "^\s+Name:"; $TR -t "$id" -f 2>/dev/null | tail -n +3)
  if echo "$icerik" | grep -qiE "$YASAK"; then
    ad=$(echo "$icerik" | grep -m1 -E "Name:" | sed 's/.*Name: //')
    $TR -t "$id" --stop >/dev/null 2>&1; $TR -t "$id" --remove-and-delete >/dev/null 2>&1
    echo "$(date '+%F %T') ENGELLENDI ve SILINDI: id=$id ad='$ad' eslesen='$(echo "$icerik" | grep -oiE "$YASAK" | head -1)'" >> $LOG
    logger -t torrent-bekci "Yasakli icerik eslesmesi: torrent $id silindi"
  fi
done
