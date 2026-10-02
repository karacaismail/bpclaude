#!/usr/bin/env python3
"""data/model.json dosyasından docs/ altındaki statik siteyi üretir. Bağımlılık yok (yalnız standart kitaplık)."""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import *  # noqa: F401,F403
import pages_extra

D = json.load(open(os.path.join(ROOT, "data", "model.json"), encoding="utf-8"))
M = D["kriterler"]
OPT = {o["id"]: o for o in D["secenekler"]}
PRJ = {p["slug"]: p for p in D["projeler"]}
OLCEK = M["kanit_olcegi"]
HEDEF = D["hedef"]
HEDEF_TL = HEDEF["hedef_usd"] * HEDEF["kur_tl_usd"]

ISARET_NOTU = ("Nakit çizgisinde hedef çentiği altı ayda %s (%s USD) net nakittir. Ölçek doğrusaldır: sol uç hedefin yarısı kadar eksi, sağ uç hedefin bir buçuk katıdır; "
               "ok, aralığın ölçeğin dışına taştığını gösterir.") % (tl(HEDEF_TL), num(HEDEF["hedef_usd"]))

aday = [o for o in D["secenekler"] if o["karar"] != "kapida-kaldi"]
yatirim = sorted(aday, key=lambda o: o["yatirim_sirasi"])
ogrenme = sorted(aday, key=lambda o: o["ogrenme_sirasi"])
kalan = [o for o in D["secenekler"] if o["karar"] == "kapida-kaldi"]


def build_assets():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    css = "".join(open(os.path.join(ROOT, "src", "styles", f), encoding="utf-8").read() for f in ("tokens.css", "base.css", "components.css"))
    open(os.path.join(OUT, "assets", "site.css"), "w", encoding="utf-8").write(minify_css(css))
    open(os.path.join(OUT, "assets", "site.js"), "w", encoding="utf-8").write(minify_js(open(os.path.join(ROOT, "src", "site.js"), encoding="utf-8").read()))
    shutil.copy(os.path.join(ROOT, "src", "favicon.svg"), os.path.join(OUT, "assets", "favicon.svg"))
    # Betik kapalıyken yüklenen tek kural: betik gerektiren araçları gizler. Betik açıkken istenmez (noscript içinde bağlanır).
    open(os.path.join(OUT, "assets", "noscript.css"), "w", encoding="utf-8").write(".filters{display:none}")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")


def deney_blok(o):
    d = o["deney"]
    return ('<dl class="dl"><div class="dl__wide"><dt>En riskli varsayım</dt><dd>%s</dd></div><div class="dl__wide"><dt>Deney</dt><dd>%s</dd></div>'
            '<div><dt>Süre ve maliyet</dt><dd>%s gün · %s kurucu saati · %s</dd></div><div><dt>Başarı ölçütü</dt><dd>%s</dd></div>'
            '<div><dt>Bırakma ölçütü</dt><dd>%s</dd></div><div><dt>Başarılıysa açılacak dilim</dt><dd>%s</dd></div></dl>') % (
        e(d["varsayim"]), e(d["yontem"]), num(d["sure_gun"]), num(d["maliyet_saat"]), tl(d["maliyet_tl"]), e(d["basari_olcutu"]), e(d["birakma_olcutu"]), e(d["sonraki_dilim"]))


def bulgular():
    """Özet sayfasındaki bulgular. Her biri (büyük sayı, payda ya da birim, başlık, açıklama) dörtlüsüdür; hepsi veriden hesaplanır."""
    import statistics as st
    O = D["secenekler"]
    net = lambda o: o["finans"]["baz"]["net_nakit"]
    sb = lambda o: o["finans"]["baz"]["saat_basi"]
    out = []
    ulasan = sum(1 for o in O if o["finans"]["hedefe_ulasir"])
    en = max(O, key=net)
    out.append((num(ulasan), "/ %s" % num(len(O)), "seçenek hedefe ulaşıyor" if ulasan else "Hedefe ulaşan seçenek yok",
                "Baz senaryoda altı ayda %s (%s USD) net nakit hedefi. En yakını %s: %s." % (tl(HEDEF_TL), num(HEDEF["hedef_usd"]), en["tanim"]["ad"], tl(net(en)))))
    eksi = sum(1 for o in O if net(o) <= 0)
    urun = [o for o in O if o["tanim"]["tur"] != "hizmet"]
    oran = lambda xs: (sum(1 for o in xs if net(o) <= 0) / float(len(xs))) if xs else 0.0
    ek = (" Hizmet dışındaki seçeneklerde (yazılım, eklenti, içerik, kod) oran %s." % pct(oran(urun))) if urun and oran(urun) > oran(O) else ""
    out.append((num(eksi), "/ %s" % num(len(O)), "Altı ayda sıfır ya da eksi nakit",
                "Bu seçeneklerde gelir geç başlıyor, sabit gider erken.%s" % ek))
    ens = max((o for o in O if sb(o) is not None), key=sb)
    gecen = sum(1 for o in O if o["finans"]["esik_gecer"])
    out.append((tl(sb(ens)), "/ saat", "En yüksek saat başı nakit",
                "Aynı saatlerde danışmanlık yapmak saatte %s bırakır. Bu eşiği baz senaryoda %s. En yükseği: %s." % (
                    tl(HEDEF["esik_saat_ucreti_tl"]), ("%d seçenek geçiyor" % gecen) if gecen else "hiçbir seçenek geçmiyor", ens["tanim"]["ad"])))
    kisa = [o for o in O if o["karar"] in ("yatirim-yap", "once-test-et")]
    hiz = sum(1 for o in kisa if o["tanim"]["tur"] == "hizmet")
    out.append((num(len(kisa)), "seçenek", "Kısa listede: önce test et" if kisa and all(o["karar"] == "once-test-et" for o in kisa) else "Kısa listede",
                ("Kısa listedeki seçeneklerin %s hizmet paketi. Büyük yatırımdan önce her birinin deney kartındaki test yapılır." % ("hepsi" if hiz == len(kisa) else "%d tanesi" % hiz)) if kisa else "Hiçbir seçenek iki koşulu birlikte sağlamıyor."))
    crit = {c["id"]: c for c in M["kriterler"]}
    ort = {cid: st.mean([o["final"][cid]["p"] for o in O if o["final"][cid].get("p") is not None]) for cid in crit}
    dusuk = sorted(ort.items(), key=lambda kv: kv[1])[:2]
    out.append((num(dusuk[0][1], 1), "/ 5", "Darboğaz kod değil, erişim ve ödeme kanıtı" if all(crit[cid]["kat"] in ("A", "B") for cid, _ in dusuk) else "En zayıf iki kriter",
                "En düşük ortalamalı iki kriter: %s (%s) ve %s (%s)." % (tr_lower(crit[dusuk[0][0]]["ad"]), num(dusuk[0][1], 1), tr_lower(crit[dusuk[1][0]]["ad"]), num(dusuk[1][1], 1))))
    odeyen = sum(p["bugun"]["odeyen_musteri"] for p in D["projeler"])
    pay = st.mean([(o["nitel"]["duzeltilmis"] / o["nitel"]["puan"]) for o in O if o["nitel"]["puan"] > 0])
    out.append((pct(pay), "", "Puanın kanıtla desteklenen payı",
                "%d projede ödeyen müşteri sayısı %d. Puanların kalanı varsayım; sıra, ilk gerçek görüşme ve tekliflerle değişecektir." % (len(D["projeler"]), odeyen)))
    return out


def bigstats_html():
    return '<ul class="bigstats">%s</ul>' % "".join(
        '<li><p class="bigstats__num">%s%s</p><p class="bigstats__title">%s</p><p class="bigstats__text">%s</p></li>' % (
            e(n), (' <span class="bigstats__den">%s</span>' % e(d)) if d else "", e(t), e(x)) for n, d, t, x in bulgular())


def dist_html():
    """Karar dağılımı: yığılmış çubuk ve altında karar başına sayı. Hücreler betik varken hızlı süzgeç düğmesine dönüşür."""
    sira = ["yatirim-yap", "once-test-et", "degistir", "beklet", "birak", "kapida-kaldi"]
    say = [(k, sum(1 for o in D["secenekler"] if o["karar"] == k)) for k in sira]
    say = [(k, n) for k, n in say if n]
    bar = '<div class="dist" aria-hidden="true">%s</div>' % "".join('<span class="dist__seg" data-karar="%s" style="--n:%d"></span>' % (k, n) for k, n in say)
    leg = '<ul class="dist-legend" id="dagilim" aria-label="Karara göre seçenek sayısı">%s</ul>' % "".join(
        '<li data-karar="%s"><span class="dist-legend__n tag" data-karar="%s">%s<span class="visually-hidden"> seçenek:</span></span> <span class="dist-legend__ad">%s</span></li>' % (
            k, k, num(n), e(D["karar_ad"][k])) for k, n in say)
    return '<h2 class="visually-hidden">Karar dağılımı</h2>' + bar + leg


def p_siralama():
    b = head("Karar ekranı", "Tüm seçenekler", None, dist_html())
    karar_order = ["once-test-et", "yatirim-yap", "degistir", "beklet", "birak", "kapida-kaldi"]
    present = [k for k in karar_order if any(o["karar"] == k for o in D["secenekler"])]
    chips = '<button type="button" class="chip" data-filter="karar" data-value="" aria-pressed="true">Tümü</button>'
    chips += "".join('<button type="button" class="chip" data-filter="karar" data-value="%s" aria-pressed="false">%s</button>' % (k, e(D["karar_ad"][k])) for k in present)
    turler = sorted(set(o["tanim"]["tur"] for o in D["secenekler"]))
    tchips = '<button type="button" class="chip" data-filter="tur" data-value="" aria-pressed="true">Tümü</button>'
    tchips += "".join('<button type="button" class="chip" data-filter="tur" data-value="%s" aria-pressed="false">%s</button>' % (e(t), e(t)) for t in turler)
    NS = {0: "Hedefe ulaşıyor", 1: "Hedefin yarısı ve üstü", 2: "Artı ama yarının altında", 3: "Sıfır ya da eksi"}
    nchips = '<button type="button" class="chip" data-filter="nsinif" data-value="" aria-pressed="true">Tümü</button>'
    nchips += "".join('<button type="button" class="chip" data-filter="nsinif" data-value="%d" aria-pressed="false">%s</button>' % (k, e(v)) for k, v in NS.items() if any(o["nakit_sinifi"] == k for o in D["secenekler"]))
    sorts = [("yatirim", "Yatırım sırası"), ("puan", "Puan"), ("nakit", "6 ay net nakit"), ("sure", "İlk tahsilat süresi"), ("ogrenme", "Öğrenme sırası"), ("stratejik", "Stratejik puan")]
    schips = "".join('<button type="button" class="chip" data-sort="%s" aria-pressed="%s">%s</button>' % (k, "true" if k == "yatirim" else "false", e(v)) for k, v in sorts)
    filt = ('<form class="filters" id="suzgec" role="search" aria-label="Seçenek süzgeçleri">'
            '<div class="field field--inline"><label for="q">Ara</label><input id="q" type="search" autocomplete="off" placeholder="Proje, müşteri ya da kanal"></div>'
            '<details class="filters__panel" id="suzgec-panel"><summary>Süz ve sırala <span class="summary__meta" id="suzgec-ozet">%d seçenek · yatırım sırası</span></summary><div class="details__body filters__body">'
            '<div class="filters__group" role="group" aria-labelledby="f-karar"><span class="filters__label" id="f-karar">Karar</span><div class="chips">%s</div></div>'
            '<div class="filters__group" role="group" aria-labelledby="f-nakit"><span class="filters__label" id="f-nakit">6 ay net nakit (baz)</span><div class="chips">%s</div></div>'
            '<div class="filters__group" role="group" aria-labelledby="f-tur"><span class="filters__label" id="f-tur">Tür</span><div class="chips">%s</div></div>'
            '<div class="filters__group" role="group" aria-labelledby="f-sort"><span class="filters__label" id="f-sort">Sırala</span><div class="chips">%s</div></div>'
            '</div></details>'
            '<p class="visually-hidden" id="sonuc" role="status" aria-live="polite">%d seçenek gösteriliyor</p>'
            '<div class="empty" id="bos" hidden><p>Bu süzgeçle eşleşen seçenek yok.</p><button type="button" class="btn btn--quiet" id="temizle">Süzgeçleri temizle</button></div></form>') % (
        len(D["secenekler"]), chips, nchips, tchips, schips, len(D["secenekler"]))
    allo = yatirim + sorted(kalan, key=lambda o: -o["nitel"]["puan"])
    rows = []
    for i, o in enumerate(allo):
        rank = str(o.get("yatirim_sirasi", "–"))
        txt = fold(" ".join([o["tanim"]["ad"], o["proje_baslik"], o["tanim"]["musteri"], o["tanim"]["kanal_birincil"], o["etiketler"]["segment"], o["tanim"]["tur"]]))
        attrs = 'data-karar="%s" data-nsinif="%d" data-tur="%s" data-yatirim="%d" data-puan="%.2f" data-nakit="%.0f" data-sure="%d" data-ogrenme="%d" data-stratejik="%.1f" data-text="%s"' % (
            o["karar"], o["nakit_sinifi"], e(o["tanim"]["tur"]), o.get("yatirim_sirasi", 9000 + i), o["nitel"]["puan"], o["finans"]["baz"]["net_nakit"], o["finans_girdi"]["ilk_tahsilat_gun"]["min"], o.get("ogrenme_sirasi", 9000 + i), o["stratejik"] or 0, e(txt))
        rows.append(opt_row(o, rank, 0, attrs))
    giris = "Her satır bir ticari seçenektir: aynı projenin farklı müşteri, fiyat ve kanal birleşimleri ayrı satırlardır."
    b += ('<div class="wrap section section--tools">%s<p class="skip-inline"><a href="#liste-baslik">Listeye geç</a></p>%s'
          '<h2 class="visually-hidden" id="liste-baslik" tabindex="-1">Seçenek listesi</h2><ol class="opts" id="liste">%s</ol></div>') % (filt, howto(giris, ISARET_NOTU), "".join(rows))
    page("siralama.html", "Sıralama", "Tüm ticari seçeneklerin kapı, puan, kanıt ve altı aylık nakit karşılaştırması.", b, "siralama.html")


def crit_rows(o, ids):
    out = []
    cdef = {c["id"]: c for c in M["kriterler"] + M["stratejik"]}
    for cid in ids:
        x = o["final"].get(cid) or {"p": None, "k": 0, "g": ""}
        a = (o["A"].get(cid) or {}).get("p"); bb = (o["B"].get(cid) or {}).get("p")
        ab = ""
        if a is not None and bb is not None and abs(a - bb) >= 2:
            ab = ' <span class="muted">İki değerlendirici ayrıştı: %d ve %d.</span>' % (a, bb)
        out.append('<li class="crit"><span class="crit__id">%s</span><span class="crit__name">%s</span><span class="crit__vals">%s%s</span><span class="crit__why">%s%s</span></li>' % (
            cid, e(cdef[cid]["ad"]), pips(x.get("p")), ev(x.get("k", 0), OLCEK), e(x.get("g", "")), ab))
    return '<ol class="crits">%s</ol>' % "".join(out)


def finans_tablo(o):
    f = o["finans"]; fi = o["finans_girdi"]
    def row(label, key, fn):
        return "<tr><th scope=\"row\">%s</th>%s</tr>" % (e(label), "".join('<td class="num">%s</td>' % fn(f[s][key]) for s in ("kotu", "baz", "iyi")))
    t = '<div class="table-wrap" tabindex="0" role="region" aria-label="Altı aylık nakit hesabı: %s"><table class="tbl tbl--tight"><thead><tr><th scope="col">6 ay</th><th scope="col" class="num">Kötü</th><th scope="col" class="num">Baz</th><th scope="col" class="num">İyi</th></tr></thead><tbody>' % e(o["tanim"]["ad"])
    t += row("Tahsilat", "tahsilat", tl) + row("Net nakit", "net_nakit", tl) + row("Net nakit (USD)", "net_usd", lambda v: num(v))
    t += row("Kurucu saati", "kurucu_saat", lambda v: num(v)) + row("Saat başı nakit", "saat_basi", tl)
    t += "</tbody></table></div>"
    ger = f["gerekli_musteri"]; ga = f["gerekli_aday"]
    facts = [
        ("Fiyat (net)", "%s · %s" % (tl(fi["net_fiyat_tl"]), e(fi["satis_tipi"]))),
        ("Kurucu saatinin bileşenleri", "satış başına %s saat · ödeme başına teslim %s saat · aylık destek %s dk" % (num(fi["satis_basina_kurucu_saati"], 0 if float(fi["satis_basina_kurucu_saati"]).is_integer() else 1), num(fi.get("teslim_saat_odeme_basina", 0), 0 if float(fi.get("teslim_saat_odeme_basina", 0)).is_integer() else 1), num(fi["musteri_basina_aylik_destek_dk"]))),
        ("Altı aylık kapasiteye sığıyor mu", ("Hayır" if f["kapasite_asimi"] else "Evet") + ": baz %s saat, kapasite %s saat" % (num(f["baz"]["kurucu_saat"]), num(f["kapasite_saat"]))),
        ("Hedef için gereken müşteri", ("%s müşteri" % num(ger, 0 if ger and ger >= 10 else 1)) if ger else "hesaplanamadı"),
        ("Gereken nitelikli aday", ("%s - %s" % (num(ga[0]), num(ga[1]))) if ga else "–"),
        ("İlk tahsilata kadar riske edilen nakit", "%s (tavan %s)" % (tl(f["riske_edilen"]), tl(HEDEF["azami_riske_edilen_nakit_tl"]))),
        ("Baz senaryo hedefe ulaşıyor mu", "Evet" if f["hedefe_ulasir"] else "Hayır: hedef %s" % tl(f["hedef_tl"])),
        ("Saat başı nakit eşiği geçiyor mu", ("Evet" if f["esik_gecer"] else "Hayır") + ": eşik %s" % tl(HEDEF["esik_saat_ucreti_tl"])),
    ]
    teslim = ('<div class="dl__wide"><dt>Teslim emeğinin dayanağı</dt><dd class="small">%s</dd></div>' % e(fi["teslim_notu"])) if fi.get("teslim_notu") else ""
    d = '<dl class="dl mt-5">%s<div class="dl__wide"><dt>Rakamların dayanağı</dt><dd class="small">%s</dd></div>%s</dl>' % (
        "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), c) for a, c in facts), e(fi["dayanak"]), teslim)
    return t + d


def secenek_blok(o):
    t = o["tanim"]; n = o["nitel"]
    s = '<div class="opt__tags mb-4">%s%s<span class="small muted">%s</span></div>' % (
        tag(o["karar"], o["karar_ad"]), gsum(o["kapi"], o["kapilar"]), e(("Yatırım sırası %d · öğrenme sırası %d" % (o["yatirim_sirasi"], o["ogrenme_sirasi"])) if "yatirim_sirasi" in o else "Sıralamaya girmiyor"))
    s += '<p class="prose">%s</p>' % e(KARAR_ACIKLAMA[o["karar"]])
    s += '<div class="split split--wide-first mt-5"><div><div class="score"><span class="score__num">%s</span><span class="score__den">/ 100 puan · kanıtla desteklenen %s · ortalama kanıt E%s · stratejik %s</span></div><div class="mt-3 mb-3">%s</div>%s</div>' % (
        num(n["puan"]), num(n["duzeltilmis"]), num(n["kanit_ort"], 1), num(o["stratejik"]) if o["stratejik"] is not None else "–", meter(n["puan"], n["duzeltilmis"], gizli=True), legend(False))
    cats = []
    for c in M["kategoriler"]:
        v = o["kategori"].get(c["id"]); vd = (o.get("kategori_duz") or {}).get(c["id"]) or 0
        cats.append('<li class="cat"><span>%s</span>%s<span class="cat__val">%s</span></li>' % (
            e(c["ad"]), meter(v or 0, vd, "%s: %s / 100; kanıtla desteklenen kısım %s" % (c["ad"], num(v or 0), num(vd))), num(v) if v is not None else "–"))
    s += '<ul class="cats">%s</ul></div>' % "".join(cats)
    fields = [("Müşteri", t["musteri"]), ("Müşterinin işi", t["is"]), ("Satın alma tetikleyicisi", t["tetikleyici"]), ("Teklif", t["teklif"]), ("Fiyat", t["fiyat"]),
              ("Birincil kanal", t["kanal_birincil"]), ("Yedek kanal", t["kanal_yedek"]), ("İlk adım", t["ilk_adim"])]
    s += '<dl class="dl mt-6">%s<div class="dl__wide"><dt>İlk satılabilir kapsam</dt><dd>%s</dd></div></dl>' % ("".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), e(c)) for a, c in fields), e(t["ilk_kapsam"]))
    gdef = {g["id"]: g for g in M["kapilar"]}
    gl = "".join('<li class="gate" data-state="%s"><span class="gate__state"><span class="dot dot--%s" aria-hidden="true"></span>%s %s</span><span class="gate__name">%s</span><span class="gate__note">%s</span></li>' % (
        v["durum"], v["durum"], g, KAPI_AD[v["durum"]], e(gdef[g]["ad"]), e(v["not"])) for g, v in sorted(o["kapilar"].items()))
    fix = ('<p class="small mt-4"><strong>Kapılar nasıl geçilir:</strong> %s</p>' % e(t["kapi_duzeltme"])) if t["kapi_duzeltme"] else ""
    s += '<h3 class="mt-6 mb-4">Kapılar</h3><ul class="gates">%s</ul>%s' % (gl, fix)
    s += '<h3 class="mt-6 mb-4">Altı aylık nakit</h3>%s%s' % (range_plot(o["finans"], True), finans_tablo(o))
    s += '<h3 class="mt-6 mb-4">Sıradaki deney</h3>%s' % deney_blok(o)
    ids = [c["id"] for c in M["kriterler"]]
    fk = o["fark"]
    uy = ("İki bağımsız değerlendirici arasındaki ortalama fark %s puan; kriterlerin %s'inde fark en çok 1." % (num(fk["ortalama"], 1), pct(fk["bir_icinde"]))) if fk["ortalama"] is not None else "Bu seçenekte tek değerlendirici puanı var."
    s += '<div class="mt-6"><details><summary>Kriter kriter puanlar (26)</summary><div class="details__body"><p class="small muted mb-3">%s</p>%s%s</div></details>' % (e(uy), ev_legend(1), crit_rows(o, ids))
    s += '<details><summary>Stratejik eksen (4)</summary><div class="details__body"><p class="small muted mb-3">Stratejik puan nakit puanıyla toplanmaz; uzun vadeli değeri ayrı gösterir.</p>%s</div></details>' % crit_rows(o, [c["id"] for c in M["stratejik"]])
    s += '<details><summary>Puanlamaya dayanak notlar</summary><div class="details__body"><p class="prose small">%s</p></div></details></div>' % e(t["kanit_notlari"])
    harf = o["id"].rsplit("-", 1)[1].upper()
    return section(t["ad"], s, None, o["id"], kicker="Seçenek %s · %s · %s" % (harf, t["tur"], o["etiketler"]["segment"]), band=(harf in "AC"))


TD = {p["slug"]: (p.get("tanitim") or {}) for p in D["projeler"]}
TR_ALFABE = "abcçdefgğhıijklmnoöpqrsştuüvwxyz"


def proje_ne(slug):
    t = TD.get(slug) or {}
    return t.get("bir_cumle") or PRJ[slug]["ozet"]


def tr_upper(ch):
    return {"i": "İ", "ı": "I"}.get(ch, ch.upper())


def tr_key(s):
    s = str(s).replace("İ", "i").replace("I", "ı").lower()
    return [TR_ALFABE.index(c) if c in TR_ALFABE else 100 + ord(c) for c in s]


def tur_grubu(tur):
    """Sözlükteki tür süzgeci için kaba grup. Türün ana ifadesine bakılır (parantezden ve "ve"den önceki kısım)."""
    import re as _re
    t = fold(tur or "")
    ana = _re.split(r" \(| ve ", t, maxsplit=1)[0]
    kurallar = [("karsilastirma", "Karşılaştırma tabanı"), (r"\boyun", "Oyun"), (r"uzanti|eklenti", "Eklenti ve uzantı"), (r"masaustu", "Masaüstü aracı"),
                (r"kod tabani|\bkit(i|leri)?\b|bilesen|sablon", "Kod, kit ve şablon"), (r"icerik|egitim|e-kitap|kurs|rehber", "İçerik ve eğitim"),
                (r"hizmet|danisman", "Hizmet"), (r"web|uygulama|yazilim|arac|panel", "Web uygulaması ve yazılım")]
    for desen, ad in kurallar:
        if _re.search(desen, ana): return ad
    return "Diğer"


def en_iyi(p):
    os_ = [OPT[i] for i in p["secenekler"]]
    sirali = [o for o in os_ if "yatirim_sirasi" in o]
    return min(sirali, key=lambda o: o["yatirim_sirasi"]) if sirali else max(os_, key=lambda o: o["nitel"]["puan"])


def funnel_html():
    O = D["secenekler"]; ES = M["karar_esikleri"]
    kapi = [o for o in O if o["kapi"]["durum"] != "kaldi"]
    uygun = [o for o in kapi if round(o["nitel"]["puan"], 6) >= ES["uygunluk_alt_puan"]]
    arti = [o for o in uygun if o["finans"]["baz"]["net_nakit"] > 0]
    kisa = [o for o in O if o["karar"] in ("yatirim-yap", "once-test-et")]
    hedef = [o for o in O if o["finans"]["hedefe_ulasir"]]
    rows = [("Değerlendirilen ticari seçenek", len(O), False), ("Hiçbir kapıda kalmayan", len(kapi), False),
            ("Uygunluk puanı en az %d" % ES["uygunluk_alt_puan"], len(uygun), False), ("Altı ayda artı nakit bırakan", len(arti), False),
            ("Hedefin en az yarısını bırakan: kısa liste", len(kisa), True), ("Hedefe ulaşan (%s USD)" % num(HEDEF["hedef_usd"]), len(hedef), True)]
    tot = float(len(O)) or 1.0
    li = "".join('<li class="funnel__row%s"><span class="funnel__label">%s</span><span class="funnel__num">%s</span>'
                  '<span class="funnel__bar" aria-hidden="true"><span class="funnel__fill" style="--w:%.1f%%"></span></span></li>' % (
                      " funnel__row--key" if key else "", e(lab), num(n), 100.0 * n / tot) for lab, n, key in rows)
    return '<ol class="funnel">%s</ol>' % li


def p_index():
    oz = D["ozet"]
    O = D["secenekler"]
    kisa = [o for o in yatirim if o["karar"] in ("yatirim-yap", "once-test-et")]
    hiz = sum(1 for o in kisa if o["tanim"]["tur"] == "hizmet")
    ulasan = sum(1 for o in O if o["finans"]["hedefe_ulasir"])
    if ulasan:
        cevap = "<strong>%d seçenek hedefe ulaşıyor.</strong> Baz senaryoda altı ayda %s USD net nakit bırakıyorlar; yine de kanıt zayıf." % (ulasan, num(HEDEF["hedef_usd"]))
    else:
        cevap = "<strong>Bugünkü haliyle hiçbiri</strong> altı ayda %s USD bırakmıyor. Sınanmaya değer %d seçenek var%s." % (
            num(HEDEF["hedef_usd"]), len(kisa), ("; %s hizmet paketi" % ("hepsi" if hiz == len(kisa) else "%d tanesi" % hiz)) if kisa else "")
    lede = ("%d proje %d ticari seçeneğe ayrıldı; her biri sekiz kapıdan geçirildi, 26 kriterde puanlandı ve altı aylık nakit hesabı yapıldı. "
            "Hiçbirinde ödeyen müşteri kanıtı yok: sıralama bir kazananı değil, sınanacak kısa bir listeyi gösterir. Önce şu sayılar okunmalı.") % (oz["proje"], oz["secenek"])
    b = ('<div class="cover on-cover"><div class="wrap cover__in"><div><p class="eyebrow">Proje seçim defteri · %s</p>'
         '<h1>Hangi proje, reklam vermeden, altı\u00a0ayda nakit getirir?</h1><p class="cover__answer">%s</p>'
         '<p class="btn-row mt-5"><a class="btn" href="#kisa-liste">Kısa listeyi gör</a><a class="btn btn--quiet" href="projeler.html">Hangi proje ne?</a></p></div>'
         '<div class="cover__figure"><h2 class="cover__caption">%d seçenekten kısa listeye</h2>%s</div></div></div>') % (e(TARIH), cevap, oz["secenek"], funnel_html())
    b += section("Ne çıktı", bigstats_html(), e(lede), "bulgular", kicker="Bulgular")
    satir = lambda os_: "".join(opt_row(o, str(o["yatirim_sirasi"]), ne=proje_ne(o["proje"])) for o in os_)
    if kisa:
        ust, alt = kisa, [o for o in yatirim if o not in kisa][:3]
        liste = '<ol class="opts" id="kisa-liste-satirlar">%s</ol>' % satir(ust)
        if alt:
            liste += ('<h3 class="opts__more">Kısa listenin hemen dışında</h3><p class="small muted">Sıradaki %d seçenek kısa liste koşullarını bugünkü haliyle sağlamıyor; '
                      'müşteri, fiyat ya da kanal değişirse listeye girebilir.</p><ol class="opts" start="%d">%s</ol>') % (len(alt), len(ust) + 1, satir(alt))
    else:
        liste = '<ol class="opts" id="kisa-liste-satirlar">%s</ol>' % satir(yatirim[:5])
    b += section("Kısa liste: yatırım sırası", howto(None, ISARET_NOTU) + liste + '<p class="btn-row mt-5"><a class="btn" href="siralama.html">Tüm sıralamayı aç</a><a class="btn btn--quiet" href="sablon.html">Puan nasıl hesaplanıyor</a></p>',
                 "Kısa listeye giren seçenek kapıda kalmamış, uygunluk tabanını geçmiş ve baz senaryoda altı ayda hedefin en az yarısını bırakan seçenektir. Sıra, kanıt düzeyiyle düzeltilmiş puana göredir.", "kisa-liste", kicker="Sıralama", band=True)
    items = []
    for o in ogrenme[:5]:
        items.append('<details><summary><span>%d. %s <span class="summary__meta">%s</span></span></summary><div class="details__body"><p class="small muted mb-4">%s</p>%s'
                     '<p class="small mt-4"><a href="proje/%s.html#%s">Seçeneğin tüm puanları</a></p></div></details>' % (
                         o["ogrenme_sirasi"], e(o["tanim"]["ad"]), e(o["proje_baslik"]), e(proje_ne(o["proje"])), deney_blok(o), e(o["proje"]), e(o["id"])))
    b += section("Önce neyi sınamalı: öğrenme sırası", "".join(items),
                 "Puanı yüksek, kanıtı zayıf ve deneyi ucuz olan seçenekler öndedir: az saatle en çok belirsizliği kapatan test önce yapılır.", "ogrenme", kicker="Deneyler")
    b += section("Nasıl okunur", layers_html("sablon.html"), "Şablon beş katmandır. Her katmanın ayrıntısı Şablon sayfasında.", "nasil", kicker="Yöntem", band=True)
    lim = ["Puan bir başarı olasılığı değildir; 70 puan, yüzde 70 başarı demek değildir.",
           "Rakamların çoğu kaynak belgelerdeki varsayımlardır; kurucunun gerçek ilişki ağı ve gerçek görüşmeler puanları değiştirir.",
           "Birinci sıradaki seçenek, yatırım yapılmaya değer olduğu için değil, diğerlerinden önde olduğu için birincidir. Karşılaştırma tabanı Portföy sayfasındadır.",
           "Doğru kullanım: kısa listeden bir ya da iki seçeneği seçip deney kartındaki testi yapmak, sonucu çalışma kitabına işleyip yeniden sıralamak."]
    b += section("Sınırlar", '<ul class="bullets prose">%s</ul>' % "".join("<li>%s</li>" % e(x) for x in lim), None, "sinirlar", kicker="Okurken")
    page("index.html", "Özet", "Reklamsız, altı ayda nakit hedefi için proje seçim defteri: kapılar, puan, kanıt ve nakit hesabı.", b, "index.html")


FORMUL = [("Ne tür bir şey", "tarayıcı uzantısı mı, web uygulaması mı, eklenti mi, hizmet paketi mi?"),
          ("Kim için", "kim kullanır, kim öder?"),
          ("Hangi işi görür", "bugün insanlar bu işi nasıl yapıyor, neye takılıyor? Projenin varlık nedeni budur."),
          ("Nasıl çalışır", "kullanıcının gözünden üç beş adım."),
          ("Bugün nerede", "fikir mi, prototip mi, canlı mı; ödeyen müşteri var mı?")]


def p_projeler():
    odeyen = sum(p["bugun"]["odeyen_musteri"] for p in D["projeler"])
    intro = ("Bir projenin ne olduğunu unuttuysanız buradan bakın. Ada dokununca tanıtımı, değerlendirmesi ve deney kartı açılır.%s") % (
        " %d projenin hiçbirinde ödeyen müşteri yok." % len(D["projeler"]) if odeyen == 0 else "")
    b = head("Proje sözlüğü", "Hangi proje ne?", e(intro))
    ornek = TD.get("qral", {}).get("bir_cumle")
    fl = "".join("<li><span><strong>%s:</strong> %s</span></li>" % (e(a), e(c)) for a, c in FORMUL)
    form = ('<div class="split"><div><ol class="formula">%s</ol></div><div class="prose"><p>Bu sözlükteki her yanıt aynı beş parçayla yazıldı. Bir projeyi başkasına anlatırken de bu sırayı kullanmak yeter: önce ne olduğunu, '
            'sonra kimin için hangi işi gördüğünü, en son bugün nerede durduğunu söyleyin.</p>%s</div></div>') % (
        fl, ('<p><strong>Örnek:</strong> %s</p>' % e(ornek)) if ornek else "")
    ps = sorted(D["projeler"], key=lambda p: tr_key(split_title(p["baslik"])[0]))
    gruplar = {}
    for p in ps:
        gruplar.setdefault(tur_grubu(TD.get(p["slug"], {}).get("tur") or ""), 0)
        gruplar[tur_grubu(TD.get(p["slug"], {}).get("tur") or "")] += 1
    chips = '<button type="button" class="chip" data-gfilter="" aria-pressed="true">Tümü</button>' + "".join(
        '<button type="button" class="chip" data-gfilter="%s" aria-pressed="false">%s <span class="chip__n">%d</span></button>' % (e(g), e(g), n) for g, n in sorted(gruplar.items(), key=lambda kv: -kv[1]))
    arac = ('<form class="filters" id="sozluk-arac" role="search" aria-label="Proje sözlüğünde ara"><div class="field field--inline"><label for="sq">Ara</label>'
            '<input id="sq" type="search" autocomplete="off" placeholder="Ad, tür ya da konu"></div>'
            '<details class="filters__panel" id="sozluk-panel"><summary>Türe göre süz <span class="summary__meta" id="sozluk-ozet">%d proje · tümü</span></summary><div class="details__body filters__body">'
            '<div class="filters__group" role="group" aria-labelledby="f-grup"><span class="filters__label" id="f-grup">Tür</span><div class="chips">%s</div></div></div></details>'
            '<p class="visually-hidden" id="sozluk-sonuc" role="status">%d proje</p>'
            '<p class="empty" id="sozluk-bos" hidden>Bu aramayla eşleşen proje yok.</p></form>') % (len(ps), chips, len(ps))
    harfler = []
    for p in ps:
        h = tr_upper(split_title(p["baslik"])[0][:1])
        if h not in harfler: harfler.append(h)
    az = '<nav class="az" aria-label="Harfe göre">%s</nav>' % "".join('<a href="#harf-%s">%s</a>' % (e(fold(h)), e(h)) for h in harfler)
    body = ""
    for h in harfler:
        items = []
        for p in [p for p in ps if tr_upper(split_title(p["baslik"])[0][:1]) == h]:
            ad, alt = split_title(p["baslik"]); t = TD.get(p["slug"], {})
            best = en_iyi(p)
            tur = t.get("tur") or alt or ""
            metin = fold(" ".join([p["baslik"], tur, t.get("bir_cumle", ""), " ".join(t.get("etiketler", []))]))
            meta = '%s<span>En iyi seçenek: %s / 100 puan · 6 ay net nakit %s%s</span>' % (
                tag(best["karar"], best["karar_ad"]), num(best["nitel"]["puan"]), tl(best["finans"]["baz"]["net_nakit"]),
                e(" · ödeyen müşteri %d" % p["bugun"]["odeyen_musteri"]) if p["bugun"]["odeyen_musteri"] else "")
            items.append('<li data-text="%s" data-grup="%s"><a class="glossary__link" href="proje/%s.html"><span class="glossary__name">%s</span><span class="glossary__type">%s</span></a>'
                         '<p class="glossary__desc">%s</p><p class="glossary__meta">%s</p></li>' % (
                             e(metin), e(tur_grubu(t.get("tur") or "")), e(p["slug"]), e(ad), e(tur), e(t.get("bir_cumle") or p["ozet"]), meta))
        body += '<section class="glossary__group" aria-labelledby="harf-%s"><h2 class="glossary__letter" id="harf-%s">%s</h2><ul class="glossary">%s</ul></section>' % (
            e(fold(h)), e(fold(h)), e(h), "".join(items))
    b += '<div class="wrap section section--tools" id="sozluk">%s%s<div id="sozluk-liste" class="glossary-cols">%s</div></div>' % (arac, az, body)
    b += section("Bir proje nasıl anlatılır", form, None, "nasil-anlatilir", kicker="Yanıt kalıbı", band=True)
    page("projeler.html", "Proje sözlüğü", "Her proje için \"bu nedir?\" sorusunun kısa yanıtı: tür, kim için, hangi iş, bugünkü durum.", b, "projeler.html")


def nedir_blok(p):
    t = p.get("tanitim")
    if not t: return ""
    adim = "".join("<li><span>%s</span></li>" % e(x) for x in t["nasil_calisir"])
    s = ('<div class="split"><div><h3>Hangi işi görür</h3><p class="mt-3">%s</p><h3 class="mt-6">Kim için</h3><p class="mt-3">%s</p>'
         '<h3 class="mt-6">Bugün nerede</h3><p class="mt-3">%s</p></div>'
         '<div><h3>Nasıl çalışır</h3><ol class="steps mt-4">%s</ol><h3 class="mt-6">Bir örnek</h3><p class="mt-3">%s</p></div></div>') % (
        e(t["sorun"]), e(t["kim_icin"]), e(t["durum"]), adim, e(t["ornek"]))
    rows = [("Nasıl para kazanır", t["para"]), ("Benzerleri", t["benzerleri"]), ("Neyle ve nerede çalışır", t["teknoloji"])]
    if t.get("ne_degil"): rows.append(("Ne değildir", t["ne_degil"]))
    if t.get("ad_nereden"): rows.append(("Adı nereden geliyor", t["ad_nereden"]))
    s += '<dl class="dl mt-6">%s</dl>' % "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), e(c)) for a, c in rows)
    return section("Bu proje nedir?", s, None, "nedir", kicker="Tanıtım")


def p_proje(p, prev_p, next_p):
    ad, alt = split_title(p["baslik"])
    t = p.get("tanitim") or {}
    best = en_iyi(p)
    grup = tur_grubu(t.get("tur") or "") if t.get("tur") else ""
    b = '<div class="masthead"><div class="wrap page-head"><div><p class="eyebrow">Proje%s</p><h1>%s</h1>' % ((" · " + e(grup)) if grup and grup != "Diğer" else "", e(ad))
    b += '<p class="answer">%s</p></div>' % e(t.get("bir_cumle") or p["ozet"] or alt or "")
    b += ('<div class="keyfacts"><div class="metric metric--best"><span class="metric__label">En iyi seçenek</span> %s <a href="#%s">%s</a></div>%s%s'
          '<div class="metric metric--gates"><span class="metric__label">Kapılar</span> %s <span class="metric__sub">ödeyen müşteri %s</span></div></div></div></div>') % (
        tag(best["karar"], best["karar_ad"]), e(best["id"]), e(best["tanim"]["ad"]), metric_score(best["nitel"]), metric_cash(best["finans"], True),
        gsum(best["kapi"], best["kapilar"], onek=False), num(p["bugun"]["odeyen_musteri"]))
    links = ([("nedir", "Bu nedir")] if t else []) + [("bugun", "Bugün"), ("iki-calisma", "İki çalışma")]
    links += [(i, "Seçenek %s" % i.rsplit("-", 1)[1].upper()) for i in p["secenekler"]]
    if p.get("hakem"): links.append(("itirazlar", "İtirazlar"))
    b += '<nav class="toc" aria-label="Bu sayfada"><div class="wrap"><div class="toc__list">%s</div></div></nav>' % "".join('<a href="#%s">%s</a>' % (e(h), e(l)) for h, l in links)
    b += nedir_blok(p)
    bugun = p["bugun"]
    var = '<ul class="bullets">%s</ul>' % "".join("<li>%s</li>" % e(x) for x in bugun["var"])
    yok = '<ul class="bullets">%s</ul>' % "".join("<li>%s</li>" % e(x) for x in bugun["yok"])
    b += section("Bugün", '<p class="prose">%s</p><div class="split mt-6"><div><h3>Var</h3><div class="mt-3">%s</div></div><div><h3>Henüz yok</h3><div class="mt-3">%s</div></div></div>'
                 '<p class="mt-5"><strong>Ödeyen müşteri: %s.</strong></p>' % (e(p["ozet"]), var, yok, num(bugun["odeyen_musteri"])), None, "bugun", kicker="Durum", band=True)
    ik = p["iki_calisma"]
    b += section("İki çalışma ne diyor", '<dl class="dl"><div><dt>Claude çalışması</dt><dd>%s</dd></div><div><dt>GPT çalışması</dt><dd>%s</dd></div><div><dt>Ayrıştıkları yer</dt><dd>%s</dd></div><div><dt>Birleşik hüküm</dt><dd>%s</dd></div>'
                 '<div class="dl__wide"><dt>Analist görüşü</dt><dd>%s</dd></div></dl>' % (e(ik["claude"]), e(ik["gpt"]), e(ik["ayrisma"]), e(ik["birlesik"]), e(p["analist_gorusu"])),
                 "Kaynak: Claude çalışmasından %d, GPT çalışmasından %d belge." % (p["kaynak"]["claude"], p["kaynak"]["gpt"]), "iki-calisma", kicker="Kaynaklar")
    for i in p["secenekler"]:
        b += secenek_blok(OPT[i])
    hk = p.get("hakem") or []
    if hk:
        AD = {"kabul": "Kabul edildi", "kismen": "Kısmen kabul edildi", "ret": "Reddedildi"}
        say = {k: sum(1 for x in hk if x["karar"] == k) for k in AD}
        rows = "".join('<li class="ruling" data-karar="%s"><span>%s</span><span class="ruling__verdict">%s</span>%s<span class="ruling__why">%s</span></li>' % (
            x["karar"], e(x["itiraz"]), AD[x["karar"]], ('<span>Değişiklik: %s</span>' % e(x["degisiklik"])) if x.get("degisiklik") else "", e(x["gerekce"])) for x in hk)
        b += section("İtirazlar ve hakem kararları", '<details><summary>%d itiraz: %d kabul, %d kısmen, %d ret</summary><div class="details__body"><ul class="rulings">%s</ul></div></details>' % (
            len(hk), say["kabul"], say["kismen"], say["ret"], rows),
            "İkinci değerlendirici, karttaki tanım, kapı ve finans girdilerinden katılmadıklarını yazdı. Her itirazı ayrı bir hakem kaynak belgeye bakarak karara bağladı; kabul edilenler karta işlendi.", "itirazlar", kicker="Denetim")
    pg = '<div class="wrap"><nav class="pager" aria-label="Projeler arası">'
    pg += ('<a class="pager__prev" href="%s.html"><small>Önceki proje</small>%s</a>' % (e(prev_p["slug"]), e(split_title(prev_p["baslik"])[0]))) if prev_p else "<span></span>"
    pg += ('<a class="pager__next" href="%s.html"><small>Sonraki proje</small>%s</a>' % (e(next_p["slug"]), e(split_title(next_p["baslik"])[0]))) if next_p else ""
    pg += "</nav></div>"
    page("proje/%s.html" % p["slug"], ad, t.get("bir_cumle") or p["ozet"], b + pg, "projeler.html", 1, ust=True)



def main():
    if os.path.isdir(OUT):
        for name in os.listdir(OUT):
            if name in ("indir",): continue
            full = os.path.join(OUT, name)
            shutil.rmtree(full) if os.path.isdir(full) else os.remove(full)
    build_assets()
    p_index(); p_siralama(); p_projeler()
    order = sorted(D["projeler"], key=lambda p: min([OPT[i].get("yatirim_sirasi", 999) for i in p["secenekler"]] + [999]))
    for i, p in enumerate(order):
        p_proje(p, order[i - 1] if i > 0 else None, order[i + 1] if i + 1 < len(order) else None)
    pages_extra.build(D, yatirim, kalan)
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print("site üretildi:", OUT, "dosya:", n)


if __name__ == "__main__":
    main()
