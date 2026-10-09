#!/bin/bash
# flugelubuntu ev klasorunu sunucuya yedekler (silinenler 30 gun .silinenler altinda tutulur)
set -u
ssh -o BatchMode=yes -o ConnectTimeout=10 flugelserver true || { echo "sunucuya ulasilamadi, atlandi"; exit 0; }
D=$(date +%F)
rsync -a --delete --partial --info=stats1 \
  --backup --backup-dir=/mnt/side/yedek/flugelubuntu/.silinenler/$D \
  --exclude='.cache/' --exclude='snap/*/common/.cache/' --exclude='.local/share/Steam/' --exclude='.steam/' \
  --exclude='.local/share/Trash/' --exclude='Downloads/' --exclude='.local/share/libvirt/images/' --exclude='*.iso' \
  -e ssh /home/flugel/ flugelserver:/mnt/side/yedek/flugelubuntu/home/; rc=$?; [ $rc -eq 24 ] && rc=0
ssh flugelserver "mkdir -p /mnt/side/yedek/flugelubuntu/.silinenler; find /mnt/side/yedek/flugelubuntu/.silinenler -mindepth 1 -maxdepth 1 -mtime +30 -exec rm -rf {} +" || true
exit ${rc:-0}
