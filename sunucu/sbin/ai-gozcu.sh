#!/bin/bash
# AI GOZCU (sistem-bakim): 15 dk'da bir hafif kontrol; sadece YENI sorun cikinca veya gunluk ozette qwen3:8b'ye sorar.
# Ollama KEEP_ALIVE=0 -> model is bitince GPU'dan bosaltilir (dusuk elektrik). Cikti: ~/sistem-bakim/durum/
set -u
OUT=/home/flugel/sistem-bakim/durum; install -d -o 1000 -g 1000 $OUT
S=/var/lib/sistem-bakim; MOD=qwen3:8b
sorun=(); bilgi=()
# GPU sanal makinedeyken (W11-GPU, kart vfio-pci'de) bu konteynerler bilerek durdurulur — sorun sayma (sistem-bakim)
GPU_KONTEYNERLER="ollama jellyfin plex immich_machine_learning subgen"
gpu_vmde(){ readlink /sys/bus/pci/devices/0000:29:00.0/driver 2>/dev/null | grep -q vfio; }
gpu_beklenen(){ gpu_vmde && [[ " $GPU_KONTEYNERLER " == *" $1 "* ]]; }
# --- kontroller ---
f=$(systemctl --failed --no-legend --plain | awk '{print $1}' | paste -sd, ); [ -n "$f" ] && sorun+=("Basarisiz servis: $f")
for c in $(docker ps -a --format '{{.Names}}|{{.Status}}' | grep -vE '\|Up' | cut -d'|' -f1); do gpu_beklenen "$c" && continue; sorun+=("Konteyner calismiyor: $c"); done
gpu_vmde && bilgi+=("GPU sanal makinede (W11-GPU): $GPU_KONTEYNERLER bilerek durduruldu")
for c in $(docker ps --format '{{.Names}}|{{.Status}}' | grep -i unhealthy | cut -d'|' -f1); do sorun+=("Konteyner sagliksiz: $c"); done
while read -r p m; do [ "${p%\%}" -ge 88 ] && sorun+=("Disk dolu: $m %${p%\%}"); done < <(df --output=pcent,target / /mnt/side /mnt/sidemain 2>/dev/null | tail -n +2)
avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ "$avail" -lt 1200 ] && sorun+=("Bellek az: ${avail}MB bos")
l5=$(awk '{print int($2)}' /proc/loadavg); [ "$l5" -ge 14 ] && sorun+=("Yuk yuksek: 5dk ort $l5")
gt=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null) || gt=NA; [ "$gt" = NA ] && ! gpu_vmde && sorun+=("GPU gorunmuyor (nvidia-smi)") ; [ "$gt" != NA ] && [ "$gt" -ge 85 ] && sorun+=("GPU sicak: ${gt}C")
ct=$(sensors 2>/dev/null | awk '/Tctl|Tdie/{gsub(/[+°C]/,"",$2); print int($2); exit}'); [ -n "$ct" ] && [ "$ct" -ge 88 ] && sorun+=("CPU sicak: ${ct}C")
vpn=$(docker inspect -f '{{.State.Health.Status}}' gluetun 2>/dev/null); [ "$vpn" != healthy ] && sorun+=("VPN (gluetun) saglikli degil: $vpn")
[ -f $S/son-kritik-yedek ] && { yas=$(( ($(date +%s) - $(date -d "$(cat $S/son-kritik-yedek)" +%s)) / 3600 )); [ $yas -ge 50 ] && sorun+=("Kritik yedek $yas saattir alinmadi"); }
[ -f $S/koruma-modu ] && sorun+=("KORUMA MODU AKTIF: $(tail -1 $S/koruma-modu) diski")
mountpoint -q /mnt/sidemain || sorun+=("Fotograf diski (/mnt/sidemain) bagli degil")
yeni_io=$(journalctl -k --since "-15min" --no-pager -o cat 2>/dev/null | grep -c "I/O error"); [ "$yeni_io" -ge 3 ] && sorun+=("Son 15 dk $yeni_io disk I/O hatasi")
tb=$(grep -c ENGELLENDI /var/log/torrent-bekci.log 2>/dev/null || echo 0)
bilgi+=("Calisma: $(uptime -p)" "Bellek bos: ${avail}MB" "Yuk: $(cut -d' ' -f1-3 /proc/loadavg)" "GPU: ${gt}C $(nvidia-smi --query-gpu=power.draw --format=csv,noheader 2>/dev/null)" "CPU: ${ct:-?}C" "Konteyner: $(docker ps -q | wc -l) calisiyor" "VPN: $vpn" "Son kritik yedek: $(cat $S/son-kritik-yedek 2>/dev/null || echo henuz yok)" "Torrent bekcisi engelleme: $tb")
while read -r p m; do bilgi+=("Disk $m: $p"); done < <(df --output=pcent,target / /mnt/side /mnt/sidemain 2>/dev/null | tail -n +2)
# --- durum dosyalari ---
durum=IYI; [ ${#sorun[@]} -gt 0 ] && durum=SORUN
{ echo "$durum"; printf '%s\n' "${sorun[@]}"; } > $OUT/.durum.yeni
ai=""
sor(){ curl -s -m 600 http://localhost:11434/api/generate -d "$(python3 -c 'import json,sys;print(json.dumps({"model":sys.argv[1],"prompt":sys.argv[2],"stream":False,"think":False,"keep_alive":0,"options":{"num_predict":350,"temperature":0.3}}))' "$MOD" "$1")" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("response","").strip())' 2>/dev/null; }
onceki=$(cat $OUT/.durum 2>/dev/null)
if [ "$durum" = SORUN ] && [ "$(cat $OUT/.durum.yeni)" != "$onceki" ]; then
  ai=$(sor "Sen bir Ubuntu ev sunucusu (Docker, Immich, Nextcloud, Jellyfin, Plex, *arr, Mullvad VPN/gluetun) yoneticisisin. Asagidaki yeni sorunlari Turkce, kisa ve maddeli acikla: olasi neden ve guvenli cozum komutu. Emin degilsen tahmin yurutme.\nSORUNLAR:\n$(printf -- '- %s\n' "${sorun[@]}")\nDURUM:\n$(printf -- '- %s\n' "${bilgi[@]}")")
  /usr/local/bin/bildirim --seviye UYARI "$(printf '%s; ' "${sorun[@]}")"
  echo "$(date '+%F %T')" > $OUT/ai-analiz.txt; echo "$ai" >> $OUT/ai-analiz.txt
elif [ "$durum" = IYI ] && [ "${onceki%%$'\n'*}" = SORUN ]; then
  /usr/local/bin/bildirim "Sorunlar giderildi, sunucu normal."
fi
mv $OUT/.durum.yeni $OUT/.durum
# gunluk ozet (09:00 civari bir kez)
if [ "$(date +%H)" = 09 ] && [ "$(cat $S/son-ozet 2>/dev/null)" != "$(date +%F)" ]; then
  date +%F > $S/son-ozet
  oz=$(sor "Turkce, 5 maddeyi gecmeyen gunluk sunucu ozeti yaz (samimi, kisa). Durum: $durum. Sorunlar: $(printf '%s; ' "${sorun[@]}"). Bilgiler: $(printf '%s; ' "${bilgi[@]}")")
  /usr/local/bin/bildirim "Gunluk ozet: $oz"; echo "$(date '+%F %T') GUNLUK OZET" > $OUT/gunluk-ozet.txt; echo "$oz" >> $OUT/gunluk-ozet.txt
fi
# HTML durum sayfasi
renk=$([ $durum = IYI ] && echo "#a6e3a1" || echo "#f38ba8")
{
cat <<H
<!doctype html><html lang="tr"><meta charset="utf-8"><meta http-equiv="refresh" content="60"><title>Sunucu Durumu</title>
<style>body{font-family:system-ui;background:#1e1e2e;color:#cdd6f4;max-width:820px;margin:24px auto;padding:0 16px}h1{font-size:22px}.d{font-size:28px;font-weight:700;color:$renk}li{margin:4px 0}.k{background:#313244;border-radius:10px;padding:12px 16px;margin:12px 0}pre{white-space:pre-wrap;font-family:inherit}small{color:#9399b2}</style>
<h1>flugelserver</h1><div class="d">$durum</div><small>Guncelleme: $(date '+%F %T') (15 dk'da bir)</small>
<div class="k"><b>Sorunlar</b><ul>$( [ ${#sorun[@]} -eq 0 ] && echo "<li>Yok</li>" || printf '<li>%s</li>' "${sorun[@]}")</ul></div>
<div class="k"><b>Sistem</b><ul>$(printf '<li>%s</li>' "${bilgi[@]}")</ul></div>
<div class="k"><b>Yapay zeka analizi (son sorun)</b><pre>$(sed 's/</\&lt;/g' $OUT/ai-analiz.txt 2>/dev/null || echo "Henuz sorun olmadi.")</pre></div>
<div class="k"><b>Gunluk ozet</b><pre>$(sed 's/</\&lt;/g' $OUT/gunluk-ozet.txt 2>/dev/null || echo "Sabah 09:00'da olusur.")</pre></div>
<div class="k"><b>Son bildirimler</b><pre>$(tail -8 $OUT/bildirimler.log 2>/dev/null | sed 's/</\&lt;/g')</pre></div>
H
} > $OUT/durum.html
chown -R 1000:1000 $OUT
