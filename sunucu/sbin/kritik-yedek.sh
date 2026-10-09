#!/bin/bash
# Kritik veri yedegi: fotograflar (Immich), Nextcloud, onemli klasorler, sunucu ayarlari -> ikinci fiziksel disk (sdc, /mnt/side)
# Silinen/degisen dosyalar 30 gun .silinenler/<tarih> altinda tutulur. (sistem-bakim)
# Kullanim: kritik-yedek.sh [--acil]   (--acil: sadece en onemliler, en hizli sekilde)
set -u
H=/mnt/side/yedek/kritik; D=$(date +%F_%H%M); KILIT=/run/kritik-yedek.lock
exec 9>$KILIT; flock -n 9 || { echo "zaten calisiyor"; exit 0; }
mountpoint -q /mnt/side && mountpoint -q /mnt/sidemain || { /usr/local/bin/bildirim --seviye HATA "Kritik yedek atlandi: diskler bagli degil"; exit 1; }
R="rsync -aHAX --delete --numeric-ids --info=stats1 --backup --backup-dir=$H/.silinenler/$D"
hata=0
# 1) Fotograflar (en oncelikli)
$R --exclude=thumbs/ --exclude=encoded-video/ /mnt/sidemain/immich/ $H/immich/ || hata=1
# 2) Nextcloud verisi
$R /mnt/sidemain/nextcloud_data/ $H/nextcloud_data/ || hata=1
# 3) Onemli klasor
$R "/mnt/sidemain/yedek amk/" "$H/yedek amk/" || hata=1
if [ "${1:-}" != "--acil" ]; then
  # 4) Sunucu ayarlari (SSD'de) - buyuk/yeniden indirilebilir kisimlar haric
  $R --exclude=ollama/ --exclude='*/cache/' --exclude='*/Cache/' --exclude='*/transcodes/' --exclude='*/Logs/' --exclude='*/logs/' --exclude='*/MediaCover/' --exclude='photoprism/' /arrapps/ $H/arrapps/ || hata=1
  $R /opt/stacks/ $H/stacks/ || hata=1
  $R /etc/ $H/etc/ || hata=1
  find $H/.silinenler -mindepth 1 -maxdepth 1 -mtime +30 -exec rm -rf {} + 2>/dev/null
fi
date '+%F %T' > /var/lib/sistem-bakim/son-kritik-yedek
[ $hata -eq 0 ] && /usr/local/bin/bildirim "Kritik yedek tamam ($(du -sh $H 2>/dev/null | cut -f1))" || /usr/local/bin/bildirim --seviye UYARI "Kritik yedek bazi hatalarla bitti, log: journalctl -u kritik-yedek"
exit $hata
