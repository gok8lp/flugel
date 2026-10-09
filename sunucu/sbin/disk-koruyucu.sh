#!/bin/bash
# OLUM ONCESI KORUMA (sistem-bakim)
# Her disk icin SMART (5 Reallocated, 187 Uncorrect, 197 Pending, 198 Offline_Uncorrectable, genel saglik) ve kernel I/O hatalarini izler.
# UYARI: bildirim.  KRITIK: koruma modu -> yazan servisleri durdur, bozulan diski salt-okunur yap,
#        once fotograflari sonra belgeleri saglam diske kopyala, haber ver, sunucuyu kapat.
# Koruma modu bir kez tetiklenir; tekrar kurmak icin: sudo rm /var/lib/sistem-bakim/koruma-modu
set -u
S=/var/lib/sistem-bakim; mkdir -p $S
BAYRAK=$S/koruma-modu
declare -A ID=( [ssd]=/dev/disk/by-id/ata-KINGSTON_SA400S37480G_50026B77828D8A00
                [foto]=/dev/disk/by-id/usb-Samsung_M3_Portable_923D7DF202000065-0:0
                [yedek]=/dev/disk/by-id/ata-ST500DM002-1BD142_Z3T34PVR )
declare -A OPT=( [ssd]="" [foto]="-d sat" [yedek]="" )
deger(){ smartctl ${OPT[$1]} -A "${ID[$1]}" 2>/dev/null | awk '$1==5||$1==187||$1==197||$1==198 {s+=$10} END{print s+0}'; }
saglik(){ smartctl ${OPT[$1]} -H "${ID[$1]}" 2>/dev/null | grep -qiE "FAILED|FAILING_NOW" && echo FAIL || echo OK; }
koruma_modu(){ # $1 disk adi
  [ -f $BAYRAK ] && return; date '+%F %T' > $BAYRAK; echo "$1" >> $BAYRAK
  /usr/local/bin/bildirim --seviye KRITIK "KORUMA MODU: $1 diski olmek uzere. Servisler durduruluyor, kritik veriler kurtariliyor, sonra sunucu KAPANACAK."
  docker ps --format '{{.Names}}' | grep -vxE 'adguardhome' | xargs -r docker stop -t 30 >/dev/null 2>&1
  case $1 in
    foto)  mount -o remount,ro /mnt/sidemain 2>/dev/null; /usr/local/sbin/kritik-yedek.sh --acil; r=$? ;;
    ssd)   /usr/local/sbin/kritik-yedek.sh; r=$? ;;
  esac
  /usr/local/bin/bildirim --seviye KRITIK "KORUMA MODU: kurtarma kopyasi bitti (kod $r). Sunucu 2 dakika icinde kapaniyor. Diski degistirmeden acmayin."
  sync; shutdown -h +2 "Disk arizasi - koruma modu"
}
for d in ssd foto yedek; do
  [ -e "${ID[$d]}" ] || { [ $d = foto ] && /usr/local/bin/bildirim --seviye UYARI "Fotograf diski (USB) gorunmuyor!"; continue; }
  dev=$(basename $(readlink -f "${ID[$d]}"))
  v=$(deger $d); h=$(saglik $d)
  [ -f $S/smart-taban-$d ] || echo "$v" > $S/smart-taban-$d
  taban=$(cat $S/smart-taban-$d); fark=$((v - taban))
  io=$(journalctl -k --since "-15min" --no-pager -o cat 2>/dev/null | grep -cE "I/O error, dev $dev\b|\[$dev\].*(FAILED Result|Medium Error|Unrecovered read)")
  echo "$(date '+%F %T') $d($dev) saglik=$h sektor=$v(taban $taban, +$fark) io15dk=$io" >> /var/log/disk-koruyucu.log
  if [ "$h" = FAIL ] || [ $fark -ge 8 ] || [ $io -ge 25 ]; then
    case $d in
      yedek) [ -f $S/yedek-disk-uyarildi ] || { /usr/local/bin/bildirim --seviye KRITIK "YEDEK DISKI (sdc) bozuluyor: saglik=$h, yeni bozuk sektor=$fark, I/O hata=$io. Yedekler durduruldu."; systemctl stop kritik-yedek.timer; touch $S/yedek-disk-uyarildi; } ;;
      *) koruma_modu $d ;;
    esac
  elif [ $fark -ge 1 ] || [ $io -ge 3 ]; then
    k=$S/uyari-$d-$fark-$(date +%F); [ -f $k ] || { /usr/local/bin/bildirim --seviye UYARI "$d diski ($dev): yeni bozuk/bekleyen sektor +$fark, son 15dk I/O hatasi $io. Izleniyor."; touch $k; }
  fi
done
# SSD omru
life=$(smartctl -A ${ID[ssd]} 2>/dev/null | awk '$1==231{print $10}'); [ -n "$life" ] && [ "$life" -le 10 ] && [ ! -f $S/ssd-omur-uyari ] && { /usr/local/bin/bildirim --seviye UYARI "SSD omru %$life kaldi - degistirmeyi planlayin"; touch $S/ssd-omur-uyari; }
exit 0
