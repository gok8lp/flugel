#!/usr/bin/env python3
"""MyAnimeList anime/manga takip botu (sistem-bakim)
- MAL listesi: izlenen + beklemedeki + planlanan anime, okunan + beklemedeki manga
- AniList: sonraki bolumun yayin saati, durum, puan; bu sezonun populer animeleri
- Bildirim: yeni bolum yayinlaninca + her sabah gunun bolumleri (bir kez)
Ortam: BOT_DIR (durum klasoru), BOT_BILDIRIM (bildirim komutu), BOT_ETIKET (mesaj on eki)
"""
import datetime as dt
import json
import os
import subprocess
import time
import urllib.request

KULLANICI = "gokalpgoksu"
DIR = os.environ.get("BOT_DIR", "/var/lib/basket-bot")
DURUM = os.path.join(DIR, "anime.json")
BILDIRIM = os.environ.get("BOT_BILDIRIM", "/usr/local/bin/bildirim")
ETIKET = os.environ.get("BOT_ETIKET", "")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) anime-takip/1.0"}


def get_json(url):
    for deneme in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25))
        except Exception:
            if deneme == 2:
                raise
            time.sleep(3)


def anilist(sorgu, degiskenler):
    req = urllib.request.Request("https://graphql.anilist.co", headers={**UA, "Content-Type": "application/json"},
                                 data=json.dumps({"query": sorgu, "variables": degiskenler}).encode())
    return json.load(urllib.request.urlopen(req, timeout=25))["data"]


def mal_liste(tur, durum):
    out, offset = [], 0
    while True:
        d = get_json(f"https://myanimelist.net/{tur}list/{KULLANICI}/load.json?status={durum}&offset={offset}")
        if not isinstance(d, list):
            break
        out += d
        if len(d) < 300:
            break
        offset += 300
        time.sleep(2)
    return out


ANIME_Q = """query($m:[Int]){Page(perPage:50){media(idMal_in:$m,type:ANIME){idMal title{romaji english}
 status averageScore episodes season seasonYear nextAiringEpisode{episode airingAt} siteUrl}}}"""
MANGA_Q = """query($m:[Int]){Page(perPage:50){media(idMal_in:$m,type:MANGA){idMal status averageScore chapters siteUrl}}}"""
TREND_Q = """query{Page(perPage:8){media(type:ANIME,status:RELEASING,sort:TRENDING_DESC,isAdult:false){idMal
 title{romaji english} averageScore nextAiringEpisode{episode airingAt} siteUrl}}}"""

DURUM_ADI = {1: "Izliyorum", 3: "Beklemede", 6: "Planliyorum"}
YAYIN = {"RELEASING": "Yayinda", "FINISHED": "Bitti", "NOT_YET_RELEASED": "Yakinda", "HIATUS": "Ara verdi", "CANCELLED": "Iptal"}


def bildir(mesaj, seviye="BILGI"):
    mesaj = (ETIKET + mesaj) if ETIKET else mesaj
    if os.environ.get("TEST"):
        print("[TEST]", mesaj.replace("\n", " | "))
        return
    subprocess.run([BILDIRIM, "--seviye", seviye, mesaj], check=False)


def main():
    os.makedirs(DIR, exist_ok=True)
    try:
        eski = json.load(open(DURUM))
    except Exception:
        eski = {"ilk": True}

    anime_ham = []
    for s in (1, 3, 6):
        for a in mal_liste("anime", s):
            a["_liste"] = s
            anime_ham.append(a)
        time.sleep(2)
    manga_ham = []
    for s in (1, 3):
        for m in mal_liste("manga", s):
            m["_liste"] = s
            manga_ham.append(m)
        time.sleep(2)

    al = {}
    ids = [a["anime_id"] for a in anime_ham]
    for i in range(0, len(ids), 50):
        for m in anilist(ANIME_Q, {"m": ids[i:i + 50]})["Page"]["media"]:
            al[m["idMal"]] = m
    alm = {}
    mids = [m["manga_id"] for m in manga_ham]
    for i in range(0, len(mids), 50):
        for m in anilist(MANGA_Q, {"m": mids[i:i + 50]})["Page"]["media"]:
            alm[m["idMal"]] = m

    simdi = int(time.time())
    anime = []
    for a in anime_ham:
        x = al.get(a["anime_id"], {})
        n = x.get("nextAiringEpisode") or {}
        durum = x.get("status") or {1: "RELEASING", 2: "FINISHED", 3: "NOT_YET_RELEASED"}.get(a.get("anime_airing_status"))
        # Planlananlardan sadece yayinda/yakinda olanlari goster
        if a["_liste"] == 6 and not n.get("airingAt"):
            continue
        if a["_liste"] == 3 and durum != "RELEASING":
            continue
        anime.append({
            "id": a["anime_id"], "ad": str(a.get("anime_title_eng") or a.get("anime_title")),
            "ad_jp": str(a.get("anime_title")), "liste": DURUM_ADI.get(a["_liste"], "?"),
            "izlenen": a.get("num_watched_episodes", 0), "toplam": a.get("anime_num_episodes") or x.get("episodes") or 0,
            "durum": YAYIN.get(durum, durum or "?"), "mal_puan": a.get("anime_score_val"),
            "al_puan": x.get("averageScore"), "benim_puan": a.get("score") or None,
            "sonraki_bolum": n.get("episode"), "yayin": n.get("airingAt"),
            "url": f"https://myanimelist.net/anime/{a['anime_id']}"})
    anime.sort(key=lambda z: (z["yayin"] is None, z["yayin"] or 0))

    manga = []
    for m in manga_ham:
        x = alm.get(m["manga_id"], {})
        manga.append({
            "id": m["manga_id"], "ad": str(m.get("manga_english") or m.get("manga_title")),
            "liste": {1: "Okuyorum", 3: "Beklemede"}.get(m["_liste"], "?"), "okunan": m.get("num_read_chapters", 0),
            "toplam": m.get("manga_num_chapters") or x.get("chapters") or 0,
            "durum": YAYIN.get(x.get("status"), {1: "Yayinda", 2: "Bitti"}.get(m.get("manga_publishing_status"), "?")),
            "mal_puan": m.get("manga_score_val"), "al_puan": x.get("averageScore"),
            "url": f"https://myanimelist.net/manga/{m['manga_id']}"})

    trend = []
    try:
        for x in anilist(TREND_Q, {})["Page"]["media"]:
            n = x.get("nextAiringEpisode") or {}
            trend.append({"ad": x["title"].get("english") or x["title"]["romaji"], "al_puan": x.get("averageScore"),
                          "sonraki_bolum": n.get("episode"), "yayin": n.get("airingAt"),
                          "url": f"https://myanimelist.net/anime/{x['idMal']}" if x.get("idMal") else x.get("siteUrl")})
    except Exception:
        trend = eski.get("trend", [])

    # --- bildirimler ---
    son_kontrol = eski.get("zaman", simdi)
    if not eski.get("ilk"):
        for e in eski.get("anime", []):
            # onceki calismada beklenen bolum artik yayinlandiysa
            if not (e.get("yayin") and son_kontrol < e["yayin"] <= simdi):
                continue
            if e["liste"] == "Planliyorum" and e.get("sonraki_bolum") == 1:
                bildir(f"🎬 Bekledigin anime basladi: {e['ad']} — 1. bolum yayinlandi! (MAL {e['mal_puan'] or '?'})")
            elif e["liste"] in ("Izliyorum", "Beklemede"):
                bildir(f"📺 Yeni bolum cikti: {e['ad']} — {e['sonraki_bolum']}. bolum"
                       f"{' (izledigin: ' + str(e['izlenen']) + ')' if e['liste'] == 'Izliyorum' else ''}")
    bugun = dt.date.today().isoformat()
    if dt.datetime.now().hour >= 8 and eski.get("son_ozet") != bugun:
        gun_sonu = int(dt.datetime.combine(dt.date.today() + dt.timedelta(days=1), dt.time()).timestamp())
        bugunku = [a for a in anime if a["yayin"] and simdi <= a["yayin"] < gun_sonu]
        if bugunku:
            satirlar = [f"• {a['ad']} {a['sonraki_bolum']}. bolum — {dt.datetime.fromtimestamp(a['yayin']).strftime('%H:%M')}" for a in bugunku]
            bildir("📺 Bugun yayinlanacak bolumler:\n" + "\n".join(satirlar))
        eski["son_ozet"] = bugun

    json.dump({"zaman": simdi, "guncelleme": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "anime": anime,
               "manga": manga, "trend": trend, "son_ozet": eski.get("son_ozet")},
              open(DURUM, "w"), ensure_ascii=False, indent=1)
    if eski.get("ilk"):
        bildir(f"📺 Anime/manga takibi basladi: {len(anime)} anime, {len(manga)} manga izleniyor.")
    print(f"anime={len(anime)} manga={len(manga)} trend={len(trend)}")


if __name__ == "__main__":
    main()
