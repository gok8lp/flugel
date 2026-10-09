#!/bin/bash
# vm-yonlendir.sh ekle|sil <ip>  — Moonlight/Apollo portlarini sunucudan (LAN + Tailscale) Windows VM'e yonlendirir.
# libvirt hook'u W11 / W11-GPU baslarken "ekle", kapaninca "sil" cagirir. (sistem-bakim)
set -u
ISLEM="$1"; IP="$2"; ETIKET="flugel-vm-$IP"
TCP="47984,47989,47990,48010"; UDP="47998:48000,48002,48010"
sil(){
  for t in nat filter; do
    iptables -t $t -S | grep -F -- "$ETIKET\"" | sed 's/^-A/-D/' | while read -r k; do eval iptables -t $t $k; done
  done
}
sil
[ "$ISLEM" = sil ] && exit 0
for ARAYUZ in enp37s0 tailscale0; do
  iptables -t nat -A PREROUTING -i $ARAYUZ -p tcp -m multiport --dports $TCP -j DNAT --to-destination $IP -m comment --comment $ETIKET
  iptables -t nat -A PREROUTING -i $ARAYUZ -p udp -m multiport --dports $UDP -j DNAT --to-destination $IP -m comment --comment $ETIKET
done
iptables -I FORWARD 1 -d $IP -o virbr0 -p tcp -m multiport --dports $TCP -j ACCEPT -m comment --comment $ETIKET
iptables -I FORWARD 1 -d $IP -o virbr0 -p udp -m multiport --dports $UDP -j ACCEPT -m comment --comment $ETIKET
