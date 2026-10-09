# FLUGEL

Kişisel bilgisayar (**flugelubuntu**, Ubuntu 26.04 / GNOME 50) ve ev sunucusu (**flugelserver**) için yazılan her şey.

## FLUGEL Akış — kişisel sosyal akış (`sunucu/panel/akis/`)
X tarzı, siyah, tek kişilik haber/sosyal akış uygulaması. Sadece Python standart kütüphanesi + sade JS.
- 36 RSS kaynağı (Türkçe ağırlıklı oyun/teknoloji/gündem, PlayStation, anime, Japonya) + 25 YouTube kanalı
- Önemli kaynaklar 1 dk, diğerleri 3 dk aralıkla (ETag ile) kontrol edilir; arayüz 20 sn'de bir yeni gönderi ekler
- Sunucudaki Ollama (gemma3): İngilizce/Japonca haberleri Türkçeye çevirir, her habere 0-100 önem puanı ve etiket verir,
  aynı olayı anlatan haberleri tek gönderide toplar, haber özetler, sohbet eder (yalnızca bağlamdaki gerçek veriyle)
- Anime/manga (AniList + MAL listesi, yasal yayın bağlantıları), Steam puan/öneri, CheapShark/Epic fiyatları,
  ESPN hafta sonu maçları, TVmaze + IMDb puanlı dizi takvimi, fragmanlar, sunucu uygulamaları
- Takip kelimeleri → uygulama içi uyarı + Telegram
- Yayın: `tailscale serve` (yalnızca tailnet) `https://flugelserver.tail42f1f4.ts.net:8443`

## Klasörler
| Klasör | İçerik |
|---|---|
| `sunucu/panel/` | Homepage paneli, `gundem-botu`, `flugel-akis` (compose) |
| `sunucu/basket-bot/` | Hakemlik ataması (ankarabasket bültenleri) ve anime/manga takip botları |
| `sunucu/sbin`, `sunucu/bin` | AI gözcü, disk koruyucu, kritik yedek, torrent bekçisi, kendini onarma, bildirim |
| `sunucu/libvirt/` | GPU passthrough (W11-GPU) libvirt hook'u + Moonlight port yönlendirme |
| `sunucu/systemd/` | Zamanlayıcılar ve servisler |
| `pc/gnome-uzantilari/` | `flugel-panel` (üst çubuk) ve `flugel-kilit` (kilit ekranı) GNOME Shell eklentileri |
| `pc/bin/` | Üst çubuk veri yardımcısı, pil modu, `w11-gpu`, `vm`, `flugel-akis` başlatıcı |
| `pc/acilis-ekrani/` | Plymouth "FLUGEL" açılış teması |
| `android/` | FLUGEL Android kabuğu (WebView, yalnızca INTERNET izni) — `derle.sh` ile Ubuntu araçlarıyla derlenir |

## Güncelleme
`./guncelle.sh "açıklama"` → PC ve sunucudaki güncel dosyaları toplar, gizli bilgileri yer tutucuyla değiştirir,
tarar (gizli bilgi kalırsa göndermez), commit'ler ve GitHub'a gönderir.

> Gizli bilgiler (Telegram token, API anahtarları, APK imza anahtarı, Cloudflare kimlikleri) depoda **yoktur**;
> betiklerde `<TELEFON>`, `<CALLMEBOT_APIKEY>`, `<GOTIFY_TOKEN>` gibi yer tutucular bulunur.
