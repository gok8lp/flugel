#!/bin/bash
# FLUGEL Akis: takip edilen kelime gecen yeni haberleri Telegram'a gonderir (sistem-bakim)
# Kaynak: /opt/stacks/panel/akis/veri/uyari.jsonl (uygulama yazar) · systemd path birimi degisince calistirir
D=/opt/stacks/panel/akis/veri/uyari.jsonl; O=/var/lib/sistem-bakim/flugel-uyari.ofs
[ -f "$D" ] || exit 0
ofs=$(cat "$O" 2>/dev/null || echo 0); boy=$(stat -c %s "$D")
[ "$boy" -lt "$ofs" ] && ofs=0
tail -c +$((ofs + 1)) "$D" | head -c $((boy - ofs)) | while IFS= read -r s; do
  m=$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); print(f"🔔 Takip: {d[\"kelime\"]}\n{d[\"baslik\"]}\n({d[\"kaynak\"]}) {d[\"link\"]}")' "$s" 2>/dev/null) || continue
  /usr/local/bin/bildirim "$m"
done
echo "$boy" > "$O"
