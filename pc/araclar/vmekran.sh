#!/bin/bash
# vmekran.sh "KEY_A KEY_B ..." [bekle_sn]  -> sunucudaki VM'e (VM=W11 varsayilan) tus gonderir, ekran goruntusu alir
# Cikti: /tmp/claude-1000/vm/ekran.png   (sistem-bakim)
VM=${VM:-W11}; mkdir -p /tmp/claude-1000/vm
ssh flugelserver "for k in $1; do sudo virsh send-key $VM \$k >/dev/null; sleep 0.4; done; sleep ${2:-3}; sudo virsh screenshot $VM /tmp/vm.ppm >/dev/null && python3 -c 'from PIL import Image; Image.open(\"/tmp/vm.ppm\").save(\"/tmp/vm.png\")'" && scp -q flugelserver:/tmp/vm.png /tmp/claude-1000/vm/ekran.png && echo ok
