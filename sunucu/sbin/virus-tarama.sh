#!/bin/bash
# Indirmeleri ve paylasilan klasorleri ClamAV ile tarar; bulunanlari karantinaya tasir (silmez). (sistem-bakim)
Q=/mnt/side/karantina; mkdir -p $Q; R=/var/log/virus-tarama.log
echo "=== $(date '+%F %T') tarama basladi" >> $R
nice -n 19 ionice -c3 clamscan -r -i --max-filesize=500M --max-scansize=1000M --move=$Q \
  /mnt/side/downloads "/mnt/sidemain/yedek amk" /mnt/sidemain/nextcloud_data /home/flugel >> $R 2>&1
n=$(tail -30 $R | grep -oP "Infected files: \K[0-9]+")
echo "=== $(date '+%F %T') bitti, enfekte: ${n:-?}" >> $R
[ "${n:-0}" -gt 0 ] && /usr/local/bin/bildirim --seviye UYARI "Virus taramasi: $n zararli dosya karantinaya alindi ($Q). Detay: $R" || /usr/local/bin/bildirim "Virus taramasi temiz"
