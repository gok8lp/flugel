#!/usr/bin/env python3
"""Ankara Basketbol fikstur botu (sistem-bakim)
ankarabasket.org.tr/fiksturler sayfasindaki tum bultenleri (Google Tablolar + Drive klasoru) indirir,
ayar dosyasindaki isim(ler)i ve takim(lar)i arar. Yeni / degisen / iptal edilen maclari Telegram'a bildirir.
Cikti: /var/lib/basket-bot/maclar.json (ust cubuk eklentisi okur)
Ayar:  /opt/basket-bot/ayar.json
"""
import datetime as dt
import os
import hashlib
import html
import io
import json
import re
import subprocess
import sys
import unicodedata
import urllib.request

import openpyxl

AYAR = os.environ.get("BOT_AYAR", "/opt/basket-bot/ayar.json")
DURUM = os.path.join(os.environ.get("BOT_DIR", "/var/lib/basket-bot"), "maclar.json")
SAYFA = "https://www.ankarabasket.org.tr/fiksturler"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) basket-bot/1.0"}


def norm(s):
    """Turkce karakter ve buyuk/kucuk harf farkini yok sayarak karsilastirma icin."""
    s = str(s).replace("İ", "i").replace("I", "ı")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def indir(url, zaman=40):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=zaman).read()


def bultenleri_bul():
    """Fikstur sayfasindan bulten adi -> indirilebilir xlsx URL listesi."""
    s = indir(SAYFA).decode("utf-8", "ignore")
    kaynaklar = []
    # Her kart: baslik ... BAGLANTI href
    for m in re.finditer(r'href="(https://(?:docs|drive)\.google\.com/[^"]+)"', s):
        url = html.unescape(m.group(1))
        on = s[max(0, m.start() - 2500):m.start()]
        on = re.sub(r"<[^>]+>", "\n", on[on.find(">") + 1:])
        satirlar = [x.strip() for x in html.unescape(on).split("\n") if x.strip() and not x.strip().startswith("<")]
        aday = [x for x in satirlar if re.search(r"(Fikst|Ma[cç]lar|Turnuva|Lig|B[uü]lten)", x) and len(x) > 10]
        baslik = aday[-1] if aday else "Bulten"
        kaynaklar.append((baslik, url))
    xlsx = []
    gorulen = set()
    for baslik, url in kaynaklar:
        if "/spreadsheets/d/" in url:
            sid = re.search(r"/d/([\w-]+)", url).group(1)
            if sid not in gorulen:
                gorulen.add(sid)
                xlsx.append((baslik, f"https://docs.google.com/spreadsheets/d/{sid}/export?format=xlsx", url))
        elif "/folders/" in url:
            fid = re.search(r"/folders/([\w-]+)", url).group(1)
            for ad, dosya_url, ac in klasor_dosyalari(fid, derinlik=2):
                if dosya_url not in gorulen:
                    gorulen.add(dosya_url)
                    xlsx.append((ad, dosya_url, ac))
    return xlsx


def klasor_dosyalari(fid, derinlik):
    s = indir(f"https://drive.google.com/embeddedfolderview?id={fid}").decode("utf-8", "ignore")
    out = []
    for dosya_id, ad in re.findall(r'/d/([\w-]+)[^"]*".*?flip-entry-title">([^<]+)<', s, re.S):
        ad = html.unescape(ad)
        if ad.lower().endswith((".xlsx", ".xls")):
            out.append((ad, f"https://drive.google.com/uc?export=download&id={dosya_id}",
                        f"https://drive.google.com/file/d/{dosya_id}/view"))
        else:  # Google Tablosu olabilir
            out.append((ad, f"https://docs.google.com/spreadsheets/d/{dosya_id}/export?format=xlsx",
                        f"https://docs.google.com/spreadsheets/d/{dosya_id}"))
    if derinlik > 0:
        for alt in set(re.findall(r"/folders/([\w-]+)", s)) - {fid}:
            try:
                out += klasor_dosyalari(alt, derinlik - 1)
            except Exception:
                pass
    return out


def tarih_yaz(v):
    if isinstance(v, dt.datetime):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, dt.date):
        return v.isoformat()
    return str(v or "").strip()


def saat_yaz(v):
    if isinstance(v, (dt.time, dt.datetime)):
        return v.strftime("%H:%M")
    s = str(v or "").strip()
    return s[:5] if re.match(r"^\d{1,2}:\d{2}", s) else s


def tara(ad, url, ac, isimler, takimlar):
    veri = indir(url, 60)
    if not veri.startswith(b"PK"):
        return []
    wb = openpyxl.load_workbook(io.BytesIO(veri), read_only=True, data_only=True)
    bulunan = []
    for ws in wb.worksheets:
        baslik = None
        for row in ws.iter_rows(values_only=True):
            hucreler = [c for c in row]
            if not any(hucreler):
                continue
            if baslik is None and sum(1 for c in hucreler if c and any(k in norm(c) for k in ("takim", "tarih", "hakem", "saat"))) >= 2:
                baslik = [norm(c) if c else "" for c in hucreler]
                baslik_ham = [str(c).strip() if c else "" for c in hucreler]
                continue
            if baslik is None:
                continue
            gorev = None
            for i, c in enumerate(hucreler):
                if c and any(n == norm(c) or n in norm(c) for n in isimler):
                    gorev = (baslik_ham[i] if i < len(baslik_ham) and baslik_ham[i] else "Görev")
            takim_eslesme = any(c and any(t in norm(c) for t in takimlar) for c in hucreler) if takimlar else False
            if not gorev and not takim_eslesme:
                continue

            def al(*anahtarlar):
                for k in anahtarlar:
                    for i, b in enumerate(baslik):
                        if k in b and i < len(hucreler) and hucreler[i] not in (None, ""):
                            return hucreler[i]
                return ""
            mac = {
                "bulten": ad, "kaynak": ac,
                "tarih": tarih_yaz(al("tarih")), "saat": saat_yaz(al("saat")),
                "salon": str(al("salon")).strip(), "lig": str(al("lig")).strip(),
                "ev": str(al("ev sahibi", "a takimi")).strip(), "dep": str(al("deplasman", "b takimi")).strip(),
                "gorev": gorev.title().replace("İ", "İ") if gorev else "Takım maçı",
                "mac_no": str(al("mac numarasi", "s no")).strip(),
            }
            mac["anahtar"] = hashlib.sha1(f'{mac["ev"]}|{mac["dep"]}|{mac["lig"]}|{mac["mac_no"]}|{mac["bulten"]}'.encode()).hexdigest()[:12]
            mac["imza"] = hashlib.sha1(f'{mac["tarih"]}|{mac["saat"]}|{mac["salon"]}|{mac["gorev"]}'.encode()).hexdigest()[:12]
            bulunan.append(mac)
    return bulunan


def bildir(mesaj, seviye="BILGI"):
    if os.environ.get("TEST"):
        print("[TEST BILDIRIM]", mesaj.replace("\n", " | ")); return
    etiket = os.environ.get("BOT_ETIKET", "")
    subprocess.run([os.environ.get("BOT_BILDIRIM", "/usr/local/bin/bildirim"), "--seviye", seviye, etiket + mesaj], check=False)


def mac_metni(m):
    return (f'🏀 {m["tarih"]} {m["saat"]} — {m["ev"]} vs {m["dep"]}\n'
            f'📍 {m["salon"]}' + (f' ({m["lig"]})' if m["lig"] else "") + f'\n👤 Gorev: {m["gorev"]}')


def main():
    os.makedirs(os.path.dirname(DURUM), exist_ok=True)
    ayar = json.load(open(AYAR))
    isimler = [norm(x) for x in ayar.get("isimler", []) if x.strip()]
    takimlar = [norm(x) for x in ayar.get("takimlar", []) if x.strip()]
    try:
        eski = json.load(open(DURUM))
    except Exception:
        eski = {"maclar": [], "ilk": True}
    eski_map = {m["anahtar"]: m for m in eski.get("maclar", [])}

    maclar, hatalar, taranan = [], [], []
    for ad, url, ac in bultenleri_bul():
        try:
            maclar += tara(ad, url, ac, isimler, takimlar)
            taranan.append(ad)
        except Exception as e:
            hatalar.append(f"{ad}: {str(e)[:60]}")
    yeni_map = {m["anahtar"]: m for m in maclar}
    bugun = dt.date.today().isoformat()

    if not eski.get("ilk"):
        for k, m in yeni_map.items():
            if k not in eski_map:
                bildir("YENI MAC ATAMASI!\n" + mac_metni(m), "UYARI")
            elif eski_map[k]["imza"] != m["imza"]:
                bildir("MAC DEGISTI!\n" + mac_metni(m) + f'\n(eskisi: {eski_map[k]["tarih"]} {eski_map[k]["saat"]} {eski_map[k]["salon"]})', "UYARI")
        for k, m in eski_map.items():
            if k not in yeni_map and m["tarih"] >= bugun:
                bildir("Mac listeden KALDIRILDI (iptal/degisiklik olabilir):\n" + mac_metni(m), "UYARI")

    gelecek = sorted([m for m in maclar if m["tarih"] >= bugun], key=lambda m: (m["tarih"], m["saat"]))
    # Mac gunu sabahi hatirlatma (07:00-10:00 arasi bir kez)
    hatirlatilan = set(eski.get("hatirlatilan", []))
    if 7 <= dt.datetime.now().hour < 10:
        for m in gelecek:
            if m["tarih"] == bugun and m["anahtar"] not in hatirlatilan:
                bildir("BUGUN MACIN VAR!\n" + mac_metni(m), "UYARI")
                hatirlatilan.add(m["anahtar"])

    json.dump({"guncelleme": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "maclar": maclar, "gelecek": gelecek,
               "taranan": taranan, "hatalar": hatalar, "isimler": ayar.get("isimler", []),
               "takimlar": ayar.get("takimlar", []), "hatirlatilan": sorted(hatirlatilan)[-50:]},
              open(DURUM, "w"), ensure_ascii=False, indent=1)
    if eski.get("ilk"):
        bildir(f"Basketbol botu calisiyor: {len(taranan)} bulten tarandi, {len(gelecek)} yaklasan mac bulundu.")
    print(f"taranan={len(taranan)} mac={len(maclar)} gelecek={len(gelecek)} hata={len(hatalar)}")
    for h in hatalar:
        print("  HATA", h, file=sys.stderr)


if __name__ == "__main__":
    main()
