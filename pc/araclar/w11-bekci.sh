#!/bin/bash
# W11 guncelleme bekcisi: UEFI'de takilma (sadece vcpu0 calisiyor, disk 0, ekran siyah, 3 dk) -> guc dongusu.
# Windows calisirken diger vcpu'lar asla tam %0 olmaz; bu yuzden Windows'u kesme riski yok. (sistem-bakim)
VM=${VM:-W11}
for tur in $(seq 1 120); do
  r=$(ssh flugelserver "VM=$VM"' 
    v1=$(virsh -c qemu:///system domstats $VM --vcpu | awk -F= "/vcpu.[1-9]+.time=/{s+=\$2} END{print s+0}")
    d1=$(virsh -c qemu:///system domblkstat $VM sdb | awk "/rd_bytes|wr_bytes/{s+=\$3} END{print s+0}")
    sleep 20
    v2=$(virsh -c qemu:///system domstats $VM --vcpu | awk -F= "/vcpu.[1-9]+.time=/{s+=\$2} END{print s+0}")
    d2=$(virsh -c qemu:///system domblkstat $VM sdb | awk "/rd_bytes|wr_bytes/{s+=\$3} END{print s+0}")
    [ "$v1" = "$v2" ] && [ "$d1" = "$d2" ] && echo TAKILI || echo CALISIYOR')
  if [ "$r" = TAKILI ]; then sayac=$((${sayac:-0}+1)); else sayac=0; fi
  if [ "${sayac:-0}" -ge 9 ]; then
    echo "$(date '+%T') UEFI takilmasi (3 dk) -> guc dongusu"
    ssh flugelserver "virsh -c qemu:///system destroy $VM; sleep 3; virsh -c qemu:///system start $VM; echo \"\$(date '+%F %T') $VM: UEFI takilmasi (bekci) -> destroy+start\" >> ~/sistem-bakim/islem-kaydi.log" >/dev/null 2>&1
    sayac=0
  fi
  ~/sistem-bakim/araclar/vmekran.sh "" 0 >/dev/null 2>&1
  # giris/kilit ekrani: genis, renkli/acik alanlar (guncelleme ekrani siyah + kucuk yazi)
  if python3 -c "
from PIL import Image,ImageStat; import sys
im=Image.open('/tmp/claude-1000/vm/ekran.png').convert('L'); sys.exit(0 if ImageStat.Stat(im).mean[0]>35 else 1)"; then
    echo "$(date '+%T') giris ekrani geldi"; exit 0
  fi
done
echo "zaman asimi"
