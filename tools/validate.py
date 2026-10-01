#!/usr/bin/env python3
"""Ajan çıktılarını doğrular.
  python3 tools/validate.py kart  data/cards/<slug>.json
  python3 tools/validate.py puan  data/scores/<slug>.A.json
  python3 tools/validate.py final data/final/<KRITER>.json
  python3 tools/validate.py hakem data/hakem/<slug>.json
  python3 tools/validate.py teslim data/teslim/<slug>.json
Çıkış kodu 0 = geçti."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forbidden import scan

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, "model", "criteria.json"), encoding="utf-8"))
MAP = {m["slug"]: m for m in json.load(open(os.path.join(ROOT, "model", "projeler.json"), encoding="utf-8"))}
CRIT = [k["id"] for k in M["kriterler"]] + [s["id"] for s in M["stratejik"]]
GATES = [g["id"] for g in M["kapilar"]]
TUR = {"yazılım ürünü", "hizmet", "içerik", "eklenti", "kod satışı", "diğer"}
SATIS = {"tek seferlik", "aylık abonelik", "yıllık peşin", "proje", "karma"}
KANAL = {"kurucu satışı", "ortak", "arama", "pazar yeri", "topluluk", "içerik", "ürün içi", "mevcut müşteri"}
REG = {"yok", "KVKK", "mevzuata bağlı", "lisans"}
errs = []


def need(cond, msg):
    if not cond: errs.append(msg)


def text(obj, key, maxlen, where, minlen=1):
    v = obj.get(key)
    need(isinstance(v, str), f"{where}.{key}: metin olmalı")
    if isinstance(v, str):
        need(len(v.strip()) >= minlen, f"{where}.{key}: boş")
        need(len(v) <= maxlen, f"{where}.{key}: {len(v)} karakter, sınır {maxlen}")


def num(obj, key, where, lo=0, hi=None):
    v = obj.get(key)
    need(isinstance(v, (int, float)) and not isinstance(v, bool), f"{where}.{key}: sayı olmalı")
    if isinstance(v, (int, float)):
        need(v >= lo, f"{where}.{key}: {v} < {lo}")
        if hi is not None: need(v <= hi, f"{where}.{key}: {v} > {hi}")


def card(d, slug):
    need(d.get("slug") == slug, f"slug dosya adıyla aynı olmalı: {slug}")
    need(slug in MAP, f"slug eşlemede yok: {slug}")
    text(d, "baslik", 120, "kart"); text(d, "ozet", 420, "kart", 60)
    b = d.get("bugun", {})
    need(isinstance(b.get("var"), list) and 1 <= len(b["var"]) <= 6, "bugun.var: 1-6 madde")
    need(isinstance(b.get("yok"), list) and 1 <= len(b["yok"]) <= 6, "bugun.yok: 1-6 madde")
    for x in (b.get("var") or []) + (b.get("yok") or []):
        need(isinstance(x, str) and len(x) <= 140, f"bugun maddesi 140 karakteri aşıyor: {str(x)[:40]}")
    num(b, "odeyen_musteri", "bugun")
    ik = d.get("iki_calisma", {})
    for k in ("claude", "gpt", "ayrisma", "birlesik"): text(ik, k, 320, "iki_calisma")
    text(d, "analist_gorusu", 280, "kart")
    S = d.get("secenekler")
    need(isinstance(S, list) and 1 <= len(S) <= 3, "secenekler: 1-3 seçenek")
    ids = set()
    for i, o in enumerate(S or []):
        w = f"secenekler[{i}]"
        oid = o.get("id", "")
        need(isinstance(oid, str) and oid.startswith(slug + "-") and oid not in ids, f"{w}.id '{slug}-a' biçiminde ve tekil olmalı")
        ids.add(oid)
        text(o, "ad", 70, w); need(o.get("tur") in TUR, f"{w}.tur: {sorted(TUR)}")
        for k, n in (("musteri", 160), ("is", 200), ("tetikleyici", 160), ("teklif", 200), ("fiyat", 120), ("kanal_birincil", 160), ("kanal_yedek", 160), ("ilk_adim", 160), ("ilk_kapsam", 240)):
            text(o, k, n, w)
        text(o, "kanit_notlari", 600, w, 80)
        need(isinstance(o.get("kapi_duzeltme"), str) and len(o["kapi_duzeltme"]) <= 200, f"{w}.kapi_duzeltme: metin, en çok 200")
        kp = o.get("kapilar", {})
        for g in GATES:
            x = kp.get(g, {})
            need(x.get("durum") in ("gecti", "test", "kaldi"), f"{w}.kapilar.{g}.durum: gecti|test|kaldi")
            text(x, "not", 160, f"{w}.kapilar.{g}")
        f = o.get("finans", {})
        need(f.get("satis_tipi") in SATIS, f"{w}.finans.satis_tipi: {sorted(SATIS)}")
        for k in ("net_fiyat_tl", "degisken_maliyet_tl", "sabit_gider_aylik_tl", "baslangic_nakit_tl", "satis_basina_kurucu_saati", "musteri_basina_aylik_destek_dk"):
            num(f, k, f"{w}.finans")
        ke = f.get("kalan_efor_saat", {})
        for k in ("min", "beklenen", "max"): num(ke, k, f"{w}.finans.kalan_efor_saat")
        if all(isinstance(ke.get(k), (int, float)) for k in ("min", "beklenen", "max")):
            need(ke["min"] <= ke["beklenen"] <= ke["max"], f"{w}.finans.kalan_efor_saat: min ≤ beklenen ≤ max")
        tg = f.get("ilk_tahsilat_gun", {})
        for k in ("min", "max"): num(tg, k, f"{w}.finans.ilk_tahsilat_gun")
        for grp in ("alti_ay_tahsilat_tl", "alti_ay_odeme_adedi", "alti_ay_musteri"):
            g3 = f.get(grp, {})
            for k in ("kotu", "baz", "iyi"): num(g3, k, f"{w}.finans.{grp}")
            if all(isinstance(g3.get(k), (int, float)) for k in ("kotu", "baz", "iyi")):
                need(g3["kotu"] <= g3["baz"] <= g3["iyi"], f"{w}.finans.{grp}: kotu ≤ baz ≤ iyi")
        dn = f.get("donusum_orani", {})
        num(dn, "dusuk", f"{w}.finans.donusum_orani", 0.0001, 1); num(dn, "yuksek", f"{w}.finans.donusum_orani", 0.0001, 1)
        text(f, "dayanak", 400, f"{w}.finans", 40)
        e = o.get("deney", {})
        for k, n in (("varsayim", 200), ("yontem", 240), ("basari_olcutu", 160), ("birakma_olcutu", 160), ("sonraki_dilim", 160)):
            text(e, k, n, f"{w}.deney")
        for k in ("sure_gun", "maliyet_saat", "maliyet_tl"): num(e, k, f"{w}.deney")
        t = o.get("etiketler", {})
        text(t, "segment", 60, f"{w}.etiketler"); text(t, "teknoloji", 60, f"{w}.etiketler")
        need(t.get("kanal_turu") in KANAL, f"{w}.etiketler.kanal_turu: {sorted(KANAL)}")
        need(t.get("regulasyon") in REG, f"{w}.etiketler.regulasyon: {sorted(REG)}")


def scores(d, slug, rater):
    need(d.get("slug") == slug, "slug dosya adıyla aynı olmalı")
    need(d.get("degerlendirici") == rater, f"degerlendirici '{rater}' olmalı")
    cp = os.path.join(ROOT, "data", "cards", slug + ".json")
    need(os.path.exists(cp), "kart dosyası yok: " + cp)
    ids = [o["id"] for o in json.load(open(cp, encoding="utf-8"))["secenekler"]] if os.path.exists(cp) else []
    P = d.get("puanlar", {})
    need(sorted(P.keys()) == sorted(ids), f"puanlar anahtarları karttaki seçenek kimlikleriyle aynı olmalı: {ids}")
    for oid, row in P.items():
        need(sorted(row.keys()) == sorted(CRIT), f"{oid}: tüm kriterler olmalı ({len(CRIT)}); eksik: {sorted(set(CRIT) - set(row.keys()))} fazla: {sorted(set(row.keys()) - set(CRIT))}")
        for c, x in row.items():
            p, k = x.get("p"), x.get("k")
            need(p is None or (isinstance(p, int) and 0 <= p <= 5), f"{oid}.{c}.p: 0-5 tam sayı ya da null")
            need(isinstance(k, int) and 0 <= k <= 4, f"{oid}.{c}.k: 0-4 tam sayı")
            g = x.get("g")
            # Herkese açık puan dosyasında gerekçe yoktur (tam sürüm private/scores_full altında); varsa 10-200 karakter olmalı.
            if "g" in x:
                need(isinstance(g, str) and 10 <= len(g) <= 200, f"{oid}.{c}.g: 10-200 karakter gerekçe")


def all_option_ids():
    out = []
    for slug in MAP:
        cp = os.path.join(ROOT, "data", "cards", slug + ".json")
        if os.path.exists(cp):
            out += [o["id"] for o in json.load(open(cp, encoding="utf-8"))["secenekler"]]
    return out


def teslim(d, slug):
    """Teslim emeği düzeltmesi: satış, teslim ve destek saatlerinin ayrıştırılmış hali."""
    need(d.get("slug") == slug, "slug dosya adıyla aynı olmalı")
    need(slug in MAP, f"slug eşlemede yok: {slug}")
    cp = os.path.join(ROOT, "data", "cards", slug + ".json")
    ids = [o["id"] for o in json.load(open(cp, encoding="utf-8"))["secenekler"]] if os.path.exists(cp) else []
    S = d.get("secenekler", {})
    need(isinstance(S, dict) and sorted(S.keys()) == sorted(ids), f"secenekler anahtarları karttaki kimliklerle aynı olmalı: {ids}")
    for oid, x in (S.items() if isinstance(S, dict) else []):
        num(x, "satis_basina_kurucu_saati", oid, 0, 400)
        num(x, "teslim_saat_odeme_basina", oid, 0, 2000)
        num(x, "musteri_basina_aylik_destek_dk", oid, 0, 6000)
        text(x, "not", 240, oid, 20)


def final(d, crit):
    need(d.get("kriter") == crit, "kriter dosya adıyla aynı olmalı: " + crit)
    need(crit in CRIT, "bilinmeyen kriter: " + crit)
    ids = all_option_ids()
    P = d.get("puanlar", {})
    eksik = sorted(set(ids) - set(P.keys())); fazla = sorted(set(P.keys()) - set(ids))
    need(not eksik, "eksik seçenek (%d): %s" % (len(eksik), eksik[:8]))
    need(not fazla, "tanınmayan seçenek (%d): %s" % (len(fazla), fazla[:8]))
    for oid, x in P.items():
        p, k, g = x.get("p"), x.get("k"), x.get("g")
        need(p is None or (isinstance(p, int) and 0 <= p <= 5), "%s.p: 0-5 tam sayı ya da null" % oid)
        need(isinstance(k, int) and 0 <= k <= 4, "%s.k: 0-4 tam sayı" % oid)
        need(isinstance(g, str) and 10 <= len(g) <= 200, "%s.g: 10-200 karakter gerekçe" % oid)


def hakem(d, slug):
    need(d.get("slug") == slug, "slug dosya adıyla aynı olmalı")
    K = d.get("kararlar")
    need(isinstance(K, list), "kararlar: liste olmalı")
    for i, x in enumerate(K or []):
        need(x.get("karar") in ("kabul", "ret", "kismen"), "kararlar[%d].karar: kabul|ret|kismen" % i)
        for k in ("itiraz", "gerekce"):
            v = x.get(k); need(isinstance(v, str) and 1 <= len(v) <= 200, "kararlar[%d].%s: 1-200 karakter" % (i, k))
        v = x.get("degisiklik"); need(isinstance(v, str) and len(v) <= 200, "kararlar[%d].degisiklik: en çok 200 karakter" % i)


def main():
    kind, path = sys.argv[1], sys.argv[2]
    raw = open(path, encoding="utf-8").read()
    try:
        d = json.loads(raw)
    except Exception as ex:
        print("JSON okunamadı:", ex); sys.exit(1)
    base = os.path.basename(path)
    if kind == "kart":
        card(d, base[:-5])
    elif kind == "final":
        final(d, base[:-5])
    elif kind == "hakem":
        hakem(d, base[:-5])
    elif kind == "teslim":
        teslim(d, base[:-5])
    else:
        slug, rater = base[:-5].rsplit(".", 1)
        scores(d, slug, rater)
    for why, word, ctx in scan(raw):
        errs.append(f"YASAK İFADE ({why}): '{word}' … {ctx}")
    if errs:
        print(f"HATA ({len(errs)}):")
        for e in errs[:60]: print(" -", e)
        sys.exit(1)
    print("GEÇTİ:", path)


if __name__ == "__main__":
    main()
