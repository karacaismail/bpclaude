#!/usr/bin/env python3
"""Kartları ve puanları birleştirir; puan, kanıt, finans, karar, sıralama ve duyarlılık hesaplarını yapar.
Çıktı: data/model.json (site ve çalışma kitabı bu dosyadan üretilir).
Kullanım: python3 tools/compute.py [--provisional]
  --provisional: kalibre edilmiş son puan yoksa A ve B'nin temkinli birleşimini kullanır."""
import glob, itertools, json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, "model", "criteria.json"), encoding="utf-8"))
MAP = json.load(open(os.path.join(ROOT, "model", "projeler.json"), encoding="utf-8"))
H = M["hedef"]
CR = M["kriterler"]
ST = M["stratejik"]
CATS = M["kategoriler"]
GUVEN = {x["kod"]: x["guven"] for x in M["kanit_olcegi"]}
BASE_CAT = {c["id"]: c["agirlik"] for c in CATS}
ES = M["karar_esikleri"]
FINAL = {}


def weights(cat_w):
    """Kategori ağırlıklarından kriter ağırlıkları: kategori ağırlığı × kriterin kategori içi payı."""
    out = {}
    for c in CR:
        out[c["id"]] = cat_w[c["kat"]] * c["agirlik"] / BASE_CAT[c["kat"]]
    return out


W_BASE = weights(BASE_CAT)


def load_scores(slug):
    res = {}
    for r in ("A", "B", "F"):
        p = os.path.join(ROOT, "data", "scores", "%s.%s.json" % (slug, r))
        if os.path.exists(p):
            res[r] = json.load(open(p, encoding="utf-8"))
    return res


HESAPLANAN = ("C1", "C2", "D1")
# Altı ayda kurucunun ayırabileceği saat: haftalık saat × ufuk (ay) × 52/12.
KAPASITE = H["haftalik_kurucu_saati"] * H["ufuk_ay"] * 52 / 12.0


ALAN = [
    ("musteri_basina_aylik_destek_dk", "aylık destek süresi"), ("satis_basina_kurucu_saati", "satış başına kurucu saati"), ("teslim_saat_odeme_basina", "ödeme başına teslim saati"),
    ("alti_ay_odeme_adedi", "altı aylık ödeme adedi"), ("alti_ay_tahsilat_tl", "altı aylık tahsilat"), ("alti_ay_tahsilat", "altı aylık tahsilat"), ("alti_ay_musteri", "altı aylık müşteri sayısı"),
    ("odeme_adedi", "ödeme adedi"), ("ilk_tahsilat_gun", "ilk tahsilat süresi"), ("ilk_tahsilat", "ilk tahsilat"), ("donusum_orani", "dönüşüm oranı"),
    ("kalan_efor_saat", "kalan efor"), ("kalan_efor", "kalan efor"), ("degisken_maliyet_tl", "değişken maliyet"), ("degisken_maliyet", "değişken maliyet"),
    ("sabit_gider_aylik_tl", "aylık sabit gider"), ("baslangic_nakit_tl", "başlangıç harcaması"), ("baslangic_nakit", "başlangıç harcaması"), ("net_fiyat_tl", "net fiyat"), ("net_fiyat", "net fiyat"),
    ("satis_tipi", "satış tipi"), ("kapi_duzeltme", "kapı düzeltme notu"), ("kanit_notlari", "kanıt notları"), ("ilk_kapsam", "ilk kapsam"), ("ilk_adim", "ilk adım"),
    ("kanal_birincil", "birincil kanal"), ("kanal_yedek", "yedek kanal"), ("kanal_turu", "kanal türü"), ("analist_gorusu", "analist görüşü"), ("sonraki_dilim", "sonraki dilim"),
    ("iki_calisma", "iki çalışma özeti"), ("odeyen_musteri", "ödeyen müşteri sayısı"), ("COMPARABLES", "karşılaştırma dosyası"),
]
import re as _re
KELIME = [(_re.compile(r"\b%s\b" % a), b) for a, b in (("kaldi", "kaldı"), ("gecti", "geçti"), ("yuksek", "yüksek"), ("dusuk", "düşük"), ("kotu", "kötü"), ("kismen", "kısmen"))]


def insan(text, slug=None):
    """Ajanların serbest metinde kullandığı ham alan adlarını ve durum kodlarını okunur Türkçeye çevirir."""
    if not isinstance(text, str) or " " not in text:
        return text
    for a, b in ALAN:
        if a in text: text = text.replace(a, b)
    for rx, b in KELIME:
        text = rx.sub(b, text)
    if slug:
        text = _re.sub(r"\b%s-([abc])\b" % _re.escape(slug), lambda m: "Seçenek " + m.group(1).upper(), text)
    return text


def insan_walk(x, slug=None):
    if isinstance(x, dict): return {k: insan_walk(v, slug) for k, v in x.items()}
    if isinstance(x, list): return [insan_walk(v, slug) for v in x]
    return insan(x, slug)


def load_hakem(slug):
    p = os.path.join(ROOT, "data", "hakem", slug + ".json")
    return json.load(open(p, encoding="utf-8")).get("kararlar", []) if os.path.exists(p) else []


def load_teslim(slug):
    """Satış, teslim ve destek saatlerinin ayrıştırılmış hali (data/teslim). Dosya yoksa teslim saati 0 sayılır."""
    p = os.path.join(ROOT, "data", "teslim", slug + ".json")
    return json.load(open(p, encoding="utf-8")).get("secenekler", {}) if os.path.exists(p) else {}


def finans_girdi(f, t):
    """Karttaki finans girdilerine teslim emeği düzeltmesini uygular; kart dosyası değişmez."""
    g = dict(f)
    g["teslim_saat_odeme_basina"] = 0
    g["teslim_notu"] = ""
    if t:
        g["satis_basina_kurucu_saati"] = t["satis_basina_kurucu_saati"]
        g["musteri_basina_aylik_destek_dk"] = t["musteri_basina_aylik_destek_dk"]
        g["teslim_saat_odeme_basina"] = t["teslim_saat_odeme_basina"]
        g["teslim_notu"] = t.get("not", "")
    return g


def load_final():
    out = {}
    for p in glob.glob(os.path.join(ROOT, "data", "final", "*.json")):
        d = json.load(open(p, encoding="utf-8"))
        out[d["kriter"]] = d.get("puanlar", {})
    return out


def trnum(v, d=0):
    s = ("{:,.%df}" % d).format(v)
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def hesaplanan(cid, fgirdi, fin, a, b):
    """C1, C2 ve D1 finans girdilerinden hesaplanır; böylece puan ile rakam çelişmez."""
    ks = [x.get("k", 0) for x in (a, b) if x]
    k = min(ks) if ks else 0
    if cid == "C1":
        lo, hi = fgirdi["ilk_tahsilat_gun"]["min"], fgirdi["ilk_tahsilat_gun"]["max"]
        mid = (lo + hi) / 2.0
        p = 5 if mid < 14 else 4 if mid < 28 else 3 if mid <= 56 else 2 if mid <= 90 else 1
        return {"p": p, "k": k, "g": "İlk tahsilat %s-%s gün; orta nokta %s gün. Finans girdisinden hesaplandı." % (trnum(lo), trnum(hi), trnum(mid))}
    if cid == "C2":
        h = fgirdi["kalan_efor_saat"]["beklenen"]; w = h / float(H["haftalik_kurucu_saati"])
        p = 5 if w < 1 else 4 if w < 3 else 3 if w <= 5 else 2 if w <= 8 else 1
        return {"p": p, "k": k, "g": "Kalan efor %s saat; haftada %d saatle %s hafta. Finans girdisinden hesaplandı." % (trnum(h), H["haftalik_kurucu_saati"], trnum(w, 1))}
    ger = fin["gerekli_musteri"]
    if ger is None:
        return {"p": None, "k": k, "g": "Müşteri başına katkı sıfır ya da eksi; gereken satış sayısı hesaplanamadı."}
    p = 5 if ger <= 5 else 4 if ger < 10 else 3 if ger <= 30 else 2 if ger < 100 else 1
    return {"p": p, "k": k, "g": "Hedef için yaklaşık %s müşteri ya da satış gerekir. Finans girdisinden hesaplandı." % trnum(ger, 0 if ger >= 10 else 1)}


def merge_ab(a, b):
    """Kalibrasyon yoksa: puanda düşük olanı, kanıtta düşük olanı al (temkinli)."""
    if a is None: return b
    if b is None: return a
    pa, pb = a.get("p"), b.get("p")
    if pa is None and pb is None: p = None
    elif pa is None: p = pb
    elif pb is None: p = pa
    else: p = min(pa, pb)
    return {"p": p, "k": min(a.get("k", 0), b.get("k", 0)), "g": (b if (pb is not None and pa is not None and pb <= pa) else a).get("g", "")}


def nitel(final, w):
    P = cov = adj = kw = 0.0
    kanitli = 0.0
    for c in CR:
        x = final.get(c["id"]) or {}
        p, k = x.get("p"), x.get("k", 0)
        wc = w[c["id"]]
        kw += wc * k
        if k >= 2: kanitli += wc
        if p is None: continue
        cov += wc
        P += wc * p / 5.0
        adj += wc * p / 5.0 * GUVEN[k]
    tot = sum(w.values())
    return {"puan": P, "kapsam": cov, "tavan": P + (tot - cov), "duzeltilmis": adj, "kanit_ort": kw / tot, "kanitli_pay": kanitli / tot}


def kat_puan(final, duzeltilmis=False):
    """Kategori puanı (0-100). duzeltilmis=True ise her kriterin katkısı kanıt güven katsayısıyla çarpılır."""
    out = {}
    for cat in CATS:
        num = den = 0.0
        for c in CR:
            if c["kat"] != cat["id"]: continue
            x = final.get(c["id"]) or {}
            if x.get("p") is None: continue
            num += c["agirlik"] * x["p"] / 5.0 * (GUVEN[x.get("k", 0)] if duzeltilmis else 1.0); den += c["agirlik"]
        out[cat["id"]] = (100.0 * num / den) if den else None
    return out


def stratejik(final):
    """Stratejik puan: ana puanla aynı kural. Boş kriter sıfır sayılmaz ama kalanlar da yüze tamamlanmaz."""
    s = 0.0; n = 0; tot = float(sum(c["agirlik"] for c in ST))
    for c in ST:
        x = final.get(c["id"]) or {}
        if x.get("p") is None: continue
        s += c["agirlik"] * x["p"] / 5.0; n += c["agirlik"]
    return (100.0 * s / tot) if n else None


def finans(f):
    out = {}
    hedef_tl = H["hedef_usd"] * H["kur_tl_usd"]
    efor = {"kotu": f["kalan_efor_saat"]["max"], "baz": f["kalan_efor_saat"]["beklenen"], "iyi": f["kalan_efor_saat"]["min"]}
    for s in ("kotu", "baz", "iyi"):
        tah = f["alti_ay_tahsilat_tl"][s]; n = f["alti_ay_odeme_adedi"][s]; mus = f["alti_ay_musteri"][s]
        net = tah - n * f["degisken_maliyet_tl"] - 6 * f["sabit_gider_aylik_tl"] - f["baslangic_nakit_tl"]
        saat = efor[s] + mus * f["satis_basina_kurucu_saati"] + n * (f.get("teslim_saat_odeme_basina", 0) + f["musteri_basina_aylik_destek_dk"] / 60.0)
        out[s] = {"tahsilat": tah, "net_nakit": net, "kurucu_saat": saat, "saat_basi": (net / saat) if saat > 0 else None, "net_usd": net / H["kur_tl_usd"]}
    b = f["alti_ay_musteri"]["baz"]
    if b > 0:
        katki = (f["alti_ay_tahsilat_tl"]["baz"] - f["alti_ay_odeme_adedi"]["baz"] * f["degisken_maliyet_tl"]) / b
    else:
        katki = f["net_fiyat_tl"] - f["degisken_maliyet_tl"]
    sabit = 6 * f["sabit_gider_aylik_tl"] + f["baslangic_nakit_tl"]
    ger = ((hedef_tl + sabit) / katki) if katki > 0 else None
    out["gerekli_musteri"] = ger
    out["gerekli_aday"] = ([ger / f["donusum_orani"]["yuksek"], ger / f["donusum_orani"]["dusuk"]] if ger else None)
    out["katki_musteri"] = katki
    out["riske_edilen"] = f["baslangic_nakit_tl"] + f["sabit_gider_aylik_tl"] * f["ilk_tahsilat_gun"]["max"] / 30.0
    out["hedef_tl"] = hedef_tl
    out["hedefe_ulasir"] = out["baz"]["net_nakit"] >= hedef_tl
    out["esik_gecer"] = (out["baz"]["saat_basi"] or 0) >= H["esik_saat_ucreti_tl"]
    out["kapasite_saat"] = KAPASITE
    out["kapasite_asimi"] = out["baz"]["kurucu_saat"] > KAPASITE
    return out


def karar(o):
    """Karar sınıfı: kapı, uygunluk puanı, kanıt ve nakit hesabına birlikte bakar."""
    g = o["kapi"]["durum"]
    # Eşik karşılaştırmalarında kayan nokta gürültüsü karar değiştirmesin (çalışma kitabıyla aynı sonuç).
    P = round(o["nitel"]["puan"], 6); S = round(o["stratejik"] or 0, 6)
    a6 = (o["final"].get("A6") or {}).get("k", 0)
    net = o["finans"]["baz"]["net_nakit"]; hedef = o["finans"]["hedef_tl"]
    uygun = P >= ES["uygunluk_alt_puan"]
    # Kurucunun altı aylık kapasitesini aşan senaryo teslim edilemez; nakit koşulunu sağlamış sayılmaz.
    nakit = net >= hedef * ES["nakit_alt_orani"] and not o["finans"]["kapasite_asimi"]
    if g == "kaldi":
        return "kapida-kaldi"
    if g == "gecti" and uygun and a6 >= ES["yatirim_kanit_kodu"] and net >= hedef:
        return "yatirim-yap"
    if uygun and nakit:
        return "once-test-et"
    if uygun or nakit:
        return "degistir"
    if S >= ES["stratejik_beklet_puan"]:
        return "beklet"
    return "birak"


KARAR_AD = {"yatirim-yap": "Yatırım yap", "once-test-et": "Önce test et", "degistir": "Değiştir", "beklet": "Beklet", "birak": "Bırak", "kapida-kaldi": "Kapıda kaldı"}
KARAR_SIRA = {"yatirim-yap": 0, "once-test-et": 1, "degistir": 2, "beklet": 3, "birak": 4, "kapida-kaldi": 5}


def ranks(vals):
    """Büyükten küçüğe sıra (1 = en yüksek)."""
    order = sorted(range(len(vals)), key=lambda i: -vals[i])
    r = [0] * len(vals)
    for pos, i in enumerate(order): r[i] = pos + 1
    return r


def spearman(a, b):
    n = len(a)
    if n < 2: return None
    ra, rb = ranks(a), ranks(b)
    d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1 - 6.0 * d2 / (n * (n * n - 1))


def main():
    provisional = "--provisional" in sys.argv
    global FINAL
    FINAL = load_final()
    projects = []; options = []
    eksik = []
    for m in MAP:
        cp = os.path.join(ROOT, "data", "cards", m["slug"] + ".json")
        if not os.path.exists(cp):
            eksik.append(m["slug"]); continue
        card = json.load(open(cp, encoding="utf-8"))
        sc = load_scores(m["slug"])
        TS = load_teslim(m["slug"])
        A = (sc.get("A") or {}).get("puanlar", {}); B = (sc.get("B") or {}).get("puanlar", {})
        proj = {k: card[k] for k in ("slug", "baslik", "ozet", "bugun", "iki_calisma", "analist_gorusu")}
        proj["kaynak"] = m["kaynak"]
        proj["itirazlar"] = {k: (sc.get("B") or {}).get(k, []) for k in ("kart_itirazlari", "kapi_itirazlari", "finans_itirazlari")}
        proj["hakem"] = load_hakem(m["slug"])
        proj = insan_walk(proj, m["slug"])
        proj["secenekler"] = []
        for o in card["secenekler"]:
            oid = o["id"]
            a, b = A.get(oid, {}), B.get(oid, {})
            fg = finans_girdi(o["finans"], TS.get(oid))
            fin = finans(fg)
            final = {}; kaynak = {}
            for c in [x["id"] for x in CR + ST]:
                if c in HESAPLANAN:
                    final[c] = hesaplanan(c, fg, fin, a.get(c), b.get(c)); kaynak[c] = "hesap"
                elif oid in FINAL.get(c, {}):
                    final[c] = FINAL[c][oid]; kaynak[c] = "kalibrasyon"
                elif provisional:
                    final[c] = merge_ab(a.get(c), b.get(c)) or {"p": None, "k": 0, "g": ""}; kaynak[c] = "gecici"
                else:
                    final[c] = a.get(c) or b.get(c) or {"p": None, "k": 0, "g": ""}; kaynak[c] = "tek"
            ds = [abs(a[c]["p"] - b[c]["p"]) for c in a if c in b and a[c].get("p") is not None and b[c].get("p") is not None]
            kd = {g: o["kapilar"][g]["durum"] for g in o["kapilar"]}
            durum = "kaldi" if "kaldi" in kd.values() else ("test" if "test" in kd.values() else "gecti")
            rec = {
                "id": oid, "proje": m["slug"], "proje_baslik": card["baslik"],
                "tanim": {k: o[k] for k in ("ad", "tur", "musteri", "is", "tetikleyici", "teklif", "fiyat", "kanal_birincil", "kanal_yedek", "ilk_adim", "ilk_kapsam", "kanit_notlari", "kapi_duzeltme")},
                "kapilar": o["kapilar"],
                "kapi": {"durum": durum, "gecti": list(kd.values()).count("gecti"), "test": list(kd.values()).count("test"), "kaldi": list(kd.values()).count("kaldi"), "kalanlar": [g for g, v in kd.items() if v == "kaldi"], "testler": [g for g, v in kd.items() if v == "test"]},
                "final": final, "A": a, "B": b, "puan_kaynagi": kaynak,
                "fark": {"ortalama": (sum(ds) / len(ds)) if ds else None, "tam_uyum": (sum(1 for d in ds if d == 0) / float(len(ds))) if ds else None, "bir_icinde": (sum(1 for d in ds if d <= 1) / float(len(ds))) if ds else None},
                "nitel": nitel(final, W_BASE), "kategori": kat_puan(final), "kategori_duz": kat_puan(final, True), "stratejik": stratejik(final),
                "finans_girdi": fg, "finans": fin,
                "deney": o["deney"], "etiketler": o["etiketler"],
            }
            for k in ("tanim", "kapilar", "final", "finans_girdi", "deney"):
                rec[k] = insan_walk(rec[k], m["slug"])
            rec["karar"] = karar(rec); rec["karar_ad"] = KARAR_AD[rec["karar"]]
            n = rec["nitel"]
            guven_orani = (n["duzeltilmis"] / n["puan"]) if n["puan"] > 0 else 0
            rec["ogrenme_endeksi"] = n["puan"] * (1 - guven_orani) / max(1.0, float(o["deney"]["maliyet_saat"]))
            options.append(rec); proj["secenekler"].append(oid)
        projects.append(proj)

    # sıralamalar
    aday = [o for o in options if o["karar"] != "kapida-kaldi"]
    def nakit_sinifi(o):
        n = o["finans"]["baz"]["net_nakit"]; h = o["finans"]["hedef_tl"]
        return 0 if n >= h else 1 if n >= h / 2.0 else 2 if n > 0 else 3
    for o in options:
        o["nakit_sinifi"] = nakit_sinifi(o)
    # Eşitlikte liste sırası korunur; kayan nokta gürültüsü sırayı etkilemesin diye yuvarlanır (çalışma kitabıyla aynı kural).
    for i, o in enumerate(sorted(aday, key=lambda o: (KARAR_SIRA[o["karar"]], -round(o["nitel"]["duzeltilmis"], 6)))):
        o["yatirim_sirasi"] = i + 1
    for i, o in enumerate(sorted(aday, key=lambda o: -round(o["ogrenme_endeksi"], 6))):
        o["ogrenme_sirasi"] = i + 1
    for i, o in enumerate(sorted(aday, key=lambda o: -round(o["nitel"]["puan"], 6))):
        o["puan_sirasi"] = i + 1

    # duyarlılık: ağırlık setleri ve her kategoride ±%20
    sets = [(w["id"], w["ad"], w["kat"]) for w in M["agirlik_setleri"]]
    for cat in BASE_CAT:
        for sign, lab in ((1.2, "+%20"), (0.8, "−%20")):
            kw = dict(BASE_CAT); kw[cat] = kw[cat] * sign
            tot = sum(kw.values()); kw = {k: 100.0 * v / tot for k, v in kw.items()}
            sets.append(("%s%s" % (cat, "p" if sign > 1 else "m"), "%s kategorisi %s" % (cat, lab), kw))
    base_scores = [o["nitel"]["puan"] for o in aday]
    duy = {"setler": [], "secenek": {}}
    all_ranks = {}
    for sid, ad, kw in sets:
        w = weights(kw)
        vals = [nitel(o["final"], w)["puan"] for o in aday]
        r = ranks(vals)
        all_ranks[sid] = r
        top5 = [aday[i]["id"] for i in sorted(range(len(aday)), key=lambda i: r[i])[:5]]
        duy["setler"].append({"id": sid, "ad": ad, "kat": kw, "spearman": spearman(base_scores, vals), "ilk5": top5})
    nset = len(sets)
    for i, o in enumerate(aday):
        rs = [all_ranks[sid][i] for sid, _, _ in sets]
        duy["secenek"][o["id"]] = {"en_iyi": min(rs), "en_kotu": max(rs), "ilk5_pay": sum(1 for x in rs if x <= 5) / float(nset), "ilk10_pay": sum(1 for x in rs if x <= 10) / float(nset),
                                  "set_sira": {sid: all_ranks[sid][i] for sid, _, _ in sets[:len(M["agirlik_setleri"])]}}

    # değerlendirici uyumu (kriter bazında)
    uyum = {}
    for c in [x["id"] for x in CR + ST]:
        ds = [abs(o["A"][c]["p"] - o["B"][c]["p"]) for o in options if c in o["A"] and c in o["B"] and o["A"][c].get("p") is not None and o["B"][c].get("p") is not None]
        uyum[c] = {"n": len(ds), "ortalama_fark": (sum(ds) / len(ds)) if ds else None, "bir_icinde": (sum(1 for d in ds if d <= 1) / float(len(ds))) if ds else None}

    ozet = {"proje": len(projects), "secenek": len(options), "eksik_kart": eksik,
            "kapi": {k: sum(1 for o in options if o["kapi"]["durum"] == k) for k in ("gecti", "test", "kaldi")},
            "karar": {KARAR_AD[k]: sum(1 for o in options if o["karar"] == k) for k in KARAR_AD},
            "hedefe_ulasan_baz": sum(1 for o in options if o["finans"]["hedefe_ulasir"]),
            "esik_gecen": sum(1 for o in options if o["finans"]["esik_gecer"]),
            "kapasite_asan": sum(1 for o in options if o["finans"]["kapasite_asimi"]),
            "teslim_duzeltmesi": sum(1 for o in options if o["finans_girdi"].get("teslim_notu")),
            "provisional": provisional, "kalibre_kriter": sorted(FINAL.keys()),
            "nakit_sinifi": {str(k): sum(1 for o in options if o.get("nakit_sinifi") == k) for k in (0, 1, 2, 3)}}
    model = {"hedef": H, "kriterler": M, "projeler": projects, "secenekler": options, "duyarlilik": duy, "uyum": uyum, "ozet": ozet, "karar_ad": KARAR_AD}
    json.dump(model, open(os.path.join(ROOT, "data", "model.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(ozet, ensure_ascii=False))


if __name__ == "__main__":
    main()
