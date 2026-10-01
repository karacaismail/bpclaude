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

aday = [o for o in D["secenekler"] if o["karar"] != "kapida-kaldi"]
yatirim = sorted(aday, key=lambda o: o["yatirim_sirasi"])
ogrenme = sorted(aday, key=lambda o: o["ogrenme_sirasi"])
kalan = [o for o in D["secenekler"] if o["karar"] == "kapida-kaldi"]


def build_assets():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    css = "".join(open(os.path.join(ROOT, "src", "styles", f), encoding="utf-8").read() for f in ("tokens.css", "base.css", "components.css"))
    open(os.path.join(OUT, "assets", "site.css"), "w", encoding="utf-8").write(minify_css(css))
    shutil.copy(os.path.join(ROOT, "src", "site.js"), os.path.join(OUT, "assets", "site.js"))
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")


def legend():
    return ('<div class="legend" aria-hidden="true"><span class="legend__item"><span class="legend__swatch"></span>kanıtla desteklenen puan</span>'
            '<span class="legend__item"><span class="legend__swatch legend__swatch--claim"></span>varsayıma dayanan puan</span></div>')


def deney_blok(o):
    d = o["deney"]
    return ('<dl class="dl"><div class="dl__wide"><dt>En riskli varsayım</dt><dd>%s</dd></div><div class="dl__wide"><dt>Deney</dt><dd>%s</dd></div>'
            '<div><dt>Süre ve maliyet</dt><dd>%s gün · %s kurucu saati · %s</dd></div><div><dt>Başarı ölçütü</dt><dd>%s</dd></div>'
            '<div><dt>Bırakma ölçütü</dt><dd>%s</dd></div><div><dt>Başarılıysa açılacak dilim</dt><dd>%s</dd></div></dl>') % (
        e(d["varsayim"]), e(d["yontem"]), num(d["sure_gun"]), num(d["maliyet_saat"]), tl(d["maliyet_tl"]), e(d["basari_olcutu"]), e(d["birakma_olcutu"]), e(d["sonraki_dilim"]))


def bulgular():
    """Özet sayfasındaki 'ne çıktı' maddeleri. Hepsi veriden hesaplanır; veri değişince metin de değişir."""
    import statistics as st
    O = D["secenekler"]
    net = lambda o: o["finans"]["baz"]["net_nakit"]
    sb = lambda o: o["finans"]["baz"]["saat_basi"]
    out = []
    ulasan = [o for o in O if o["finans"]["hedefe_ulasir"]]
    en = max(O, key=net)
    if ulasan:
        out.append(("Hedefe ulaşan seçenek", "Baz senaryoda %d seçenek altı ayda %s net nakde ulaşıyor. En yükseği %s (%s)." % (len(ulasan), tl(HEDEF_TL), en["tanim"]["ad"], tl(net(en)))))
    else:
        out.append(("Hedefe ulaşan seçenek yok", "Baz senaryoda hiçbir seçenek altı ayda %s (%s USD) net nakde ulaşmıyor. En yakını %s: %s. %d seçeneğin %d tanesinde altı aylık net nakit sıfır ya da eksi." % (
            tl(HEDEF_TL), num(HEDEF["hedef_usd"]), en["tanim"]["ad"], tl(net(en)), len(O), sum(1 for o in O if net(o) <= 0))))
    olan = [o for o in O if sb(o) is not None]
    ens = max(olan, key=sb)
    gecen = sum(1 for o in O if o["finans"]["esik_gecer"])
    out.append(("Saat ücretini geçen seçenek yok" if not gecen else "Saat ücretini geçen %d seçenek var" % gecen,
                "Aynı saatlerde danışmanlık yapmak saatte %s bırakır. Bu eşiği baz senaryoda %s. En yüksek saat başı nakit %s ile %s." % (
                    tl(HEDEF["esik_saat_ucreti_tl"]), ("%d seçenek geçiyor" % gecen) if gecen else "hiçbir seçenek geçmiyor", tl(sb(ens)), ens["tanim"]["ad"])))
    kisa = [o for o in O if o["karar"] in ("yatirim-yap", "once-test-et")]
    kopya = [o for o in O if o["tanim"]["tur"] in ("yazılım ürünü", "eklenti", "içerik")]
    hiz = sum(1 for o in kisa if o["tanim"]["tur"] == "hizmet")
    if kisa:
        out.append(("Kısa listede hizmetler var", "Kısa listedeki %d seçeneğin %d tanesi hizmet paketi. Kopyası satılan ürünlerin (yazılım, eklenti, içerik) %d tanesinden %d tanesi altı ayda sıfır ya da eksi nakit bırakıyor: gelir geç başlıyor, sabit gider erken." % (
            len(kisa), hiz, len(kopya), sum(1 for o in kopya if net(o) <= 0))))
    crit = {c["id"]: c for c in M["kriterler"]}
    ort = {cid: st.mean([o["final"][cid]["p"] for o in O if o["final"][cid].get("p") is not None]) for cid in crit}
    dusuk = sorted(ort.items(), key=lambda kv: kv[1])[:2]
    kat = {k["id"]: st.mean([o["kategori"][k["id"]] for o in O if o["kategori"].get(k["id"]) is not None]) for k in M["kategoriler"]}
    kd = min(kat.items(), key=lambda kv: kv[1]); kad = {k["id"]: k["ad"] for k in M["kategoriler"]}
    out.append(("Darboğaz kod değil, alıcıya erişim ve ödeme kanıtı", "En düşük ortalamalı iki kriter %s (%s / 5) ve %s (%s / 5). Kategorilerde en zayıf olan %s: ortalama %s / 100." % (
        crit[dusuk[0][0]]["ad"].lower(), num(dusuk[0][1], 1), crit[dusuk[1][0]]["ad"].lower(), num(dusuk[1][1], 1), kad[kd[0]].lower(), num(kd[1]))))
    odeyen = sum(p["bugun"]["odeyen_musteri"] for p in D["projeler"])
    kort = st.mean([o["nitel"]["kanit_ort"] for o in O])
    out.append(("Puanların çoğu varsayım", "%d projede ödeyen müşteri sayısı %d. Puanların ağırlıklı kanıt ortalaması E%s; çubuklardaki taralı kısım bu yüzden geniş. Sıra, ilk gerçek görüşme ve tekliflerle değişecektir." % (
        len(D["projeler"]), odeyen, num(kort, 1))))
    return out


def p_index():
    oz = D["ozet"]
    lede = ("İki ayrı çalışmanın ele aldığı %d proje %d ticari seçeneğe ayrıldı. Her seçenek sekiz kapıdan geçirildi, 26 kriterde puanlandı ve altı aylık nakit hesabı yapıldı. "
            "Hiçbir seçenekte ödeyen müşteri kanıtı yok; bu yüzden sonuç bir kazanan değil, sınanacak kısa bir listedir.") % (oz["proje"], oz["secenek"])
    b = head("Proje seçim defteri · %s" % TARIH, "Hangi proje, reklam vermeden, altı ayda nakit getirir?", e(lede))
    stats = [
        (num(oz["secenek"]), "ticari seçenek değerlendirildi"),
        (num(oz["kapi"]["kaldi"]), "seçenek bir kapıda kaldı"),
        (num(oz["karar"].get("Önce test et", 0)), "seçenek kısa listede: önce test et"),
        (num(oz["hedefe_ulasan_baz"]), "seçenek baz senaryoda %s USD hedefine ulaşıyor" % num(HEDEF["hedef_usd"])),
    ]
    b += '<div class="wrap"><div class="stats">%s</div></div>' % "".join('<div class="stat"><p class="stat__num">%s</p><p class="stat__label">%s</p></div>' % (a, e(c)) for a, c in stats)
    b += section("Ne çıktı", '<dl class="dl findings">%s</dl>' % "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), e(c)) for a, c in bulgular()),
                 "Sayılar aşağıdaki listelerden önce okunmalı: sıralama, hiçbirinin hedefe ulaşmadığı seçenekler arasındaki sıralamadır.", "bulgular")
    rows = "".join(opt_row(o, str(o["yatirim_sirasi"])) for o in yatirim[:7])
    b += section("Kısa liste: yatırım sırası", legend() + '<ol class="opts">%s</ol><p class="btn-row mt-5"><a class="btn" href="siralama.html">Tüm sıralamayı aç</a><a class="btn btn--quiet" href="sablon.html">Puan nasıl hesaplanıyor</a></p>' % rows,
                 "Kısa listeye giren seçenek kapıda kalmamış, uygunluk tabanını geçmiş ve baz senaryoda altı ayda hedefin en az yarısını bırakan seçenektir. Sıra, kanıt düzeyiyle düzeltilmiş puana göredir; rakamlar kaynak belgelerdeki varsayımlardan türetilmiştir.", "kisa-liste")
    items = []
    for o in ogrenme[:5]:
        items.append('<details><summary><span>%d. %s <span class="summary__meta">%s</span></span></summary><div class="details__body">%s'
                     '<p class="small mt-4"><a href="proje/%s.html#%s">Seçeneğin tüm puanları</a></p></div></details>' % (
                         o["ogrenme_sirasi"], e(o["tanim"]["ad"]), e(o["proje_baslik"]), deney_blok(o), e(o["proje"]), e(o["id"])))
    b += section("Önce neyi sınamalı: öğrenme sırası", "".join(items),
                 "Yatırım sırası ile öğrenme sırası aynı şey değildir. Burada puanı yüksek, kanıtı zayıf ve deneyi ucuz olan seçenekler öndedir: az saatle en çok belirsizliği kapatan test önce yapılır.", "ogrenme")
    how = [
        ("Kapılar", "Sekiz koşul telafi edilemez: haklar, hukuk, tahsilat yolu, ödeyecek alıcı, reklamsız kanal, süre, riske edilen nakit, standart teslim. Biri kaldıysa puan ne olursa olsun seçenek sıralamaya girmez; bilinmeyen koşul sıfır puan değil, testtir."),
        ("Puan", "26 kriter altı kategoride toplanır. Her kriter 0-5 arası, davranışla tanımlanmış çapalara göre puanlanır; kategori ağırlığı kriterlere dağıtılır, ek kategori puanı verilmez."),
        ("Kanıt", "Her puanın yanında kanıt düzeyi durur: varsayımdan (E0) tekrarlanan ödemeye (E4). Çubuğun dolu kısmı kanıtla desteklenen, taralı kısmı varsayıma dayanan puandır."),
        ("Nakit", "Puan parayı göstermez. Her seçenek için altı aylık tahsilat, maliyet ve kurucu saati kötü, baz ve iyi senaryoda ayrıca hesaplanır; saat başı nakit, eşik saat ücretiyle karşılaştırılır."),
    ]
    b += section("Nasıl okunur", '<dl class="dl">%s</dl>' % "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), e(c)) for a, c in how), None, "nasil")
    lim = ["Puan bir başarı olasılığı değildir; 70 puan, yüzde 70 başarı demek değildir.",
           "Rakamların çoğu kaynak belgelerdeki varsayımlardır; kurucunun gerçek ilişki ağı ve gerçek görüşmeler puanları değiştirir.",
           "Birinci sıradaki seçenek, yatırım yapılmaya değer olduğu için değil, diğerlerinden önde olduğu için birincidir. Karşılaştırma tabanı Portföy sayfasındadır.",
           "Doğru kullanım: kısa listeden bir ya da iki seçeneği seçip deney kartındaki testi yapmak, sonucu çalışma kitabına işleyip yeniden sıralamak."]
    b += section("Sınırlar", '<ul class="bullets prose">%s</ul>' % "".join("<li>%s</li>" % e(x) for x in lim), None, "sinirlar")
    page("index.html", "Özet", "Reklamsız, altı ayda nakit hedefi için proje seçim defteri: kapılar, puan, kanıt ve nakit hesabı.", b, "index.html")


def p_siralama():
    b = head("Karar ekranı", "Tüm seçenekler", "Her satır bir ticari seçenektir: aynı projenin farklı müşteri, fiyat ve kanal birleşimleri ayrı satırlardır. Süzgeçler ve sıralama düğmeleri listeyi yeniden düzenler.")
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
    filt = ('<form class="filters" id="suzgec" role="search" aria-label="Seçenek süzgeçleri" hidden>'
            '<div class="field"><label for="q">Ara</label><input id="q" type="search" autocomplete="off" placeholder="Proje, müşteri ya da kanal"></div>'
            '<details class="filters__panel" id="suzgec-panel"><summary>Süzgeç ve sıralama <span class="muted small" id="suzgec-ozet">Tümü · yatırım sırası</span></summary><div class="details__body filters__body">'
            '<div class="filters__group" role="group" aria-labelledby="f-karar"><span class="filters__label" id="f-karar">Karar</span><div class="chips">%s</div></div>'
            '<div class="filters__group" role="group" aria-labelledby="f-nakit"><span class="filters__label" id="f-nakit">6 ay net nakit (baz)</span><div class="chips">%s</div></div>'
            '<div class="filters__group" role="group" aria-labelledby="f-tur"><span class="filters__label" id="f-tur">Tür</span><div class="chips">%s</div></div>'
            '<div class="filters__group" role="group" aria-labelledby="f-sort"><span class="filters__label" id="f-sort">Sırala</span><div class="chips">%s</div></div>'
            '</div></details>'
            '<p class="result-count" id="sonuc" role="status" aria-live="polite">%d seçenek gösteriliyor</p>'
            '<div class="empty" id="bos" hidden><p>Bu süzgeçle eşleşen seçenek yok.</p><button type="button" class="btn btn--quiet" id="temizle">Süzgeçleri temizle</button></div></form>') % (chips, nchips, tchips, schips, len(D["secenekler"]))
    allo = yatirim + sorted(kalan, key=lambda o: -o["nitel"]["puan"])
    rows = []
    for i, o in enumerate(allo):
        rank = str(o.get("yatirim_sirasi", "–"))
        txt = fold(" ".join([o["tanim"]["ad"], o["proje_baslik"], o["tanim"]["musteri"], o["tanim"]["kanal_birincil"], o["etiketler"]["segment"], o["tanim"]["tur"]]))
        attrs = 'data-karar="%s" data-nsinif="%d" data-tur="%s" data-yatirim="%d" data-puan="%.2f" data-nakit="%.0f" data-sure="%d" data-ogrenme="%d" data-stratejik="%.1f" data-text="%s"' % (
            o["karar"], o["nakit_sinifi"], e(o["tanim"]["tur"]), o.get("yatirim_sirasi", 9000 + i), o["nitel"]["puan"], o["finans"]["baz"]["net_nakit"], o["finans_girdi"]["ilk_tahsilat_gun"]["min"], o.get("ogrenme_sirasi", 9000 + i), o["stratejik"] or 0, e(txt))
        rows.append(opt_row(o, rank, 0, attrs))
    b += '<div class="wrap">%s<h2 class="visually-hidden">Seçenek listesi</h2>%s<ol class="opts" id="liste">%s</ol></div>' % (filt, legend(), "".join(rows))
    page("siralama.html", "Sıralama", "Tüm ticari seçeneklerin kapı, puan, kanıt ve altı aylık nakit karşılaştırması.", b, "siralama.html")


def p_projeler():
    b = head("Projeler", "Proje proje", "Her proje bir ya da birkaç ticari seçenek olarak değerlendirildi. Proje sayfasında iki çalışmanın ne dediği, seçenek tanımları, kapılar, kriter kriter puanlar, nakit hesabı ve deney kartı var.")
    items = []
    for p in sorted(D["projeler"], key=lambda p: min([OPT[i].get("yatirim_sirasi", 999) for i in p["secenekler"]] + [999])):
        os_ = [OPT[i] for i in p["secenekler"]]
        best = max(os_, key=lambda o: o["nitel"]["puan"])
        kal = sum(1 for o in os_ if o["karar"] == "kapida-kaldi")
        meta = "%d seçenek · en yüksek puan %s" % (len(os_), num(best["nitel"]["puan"]))
        if kal == len(os_): meta = "%d seçenek · hepsi kapıda kaldı" % len(os_)
        items.append('<li><a href="proje/%s.html"><span class="linklist__title">%s</span><span class="linklist__meta">%s</span><span class="linklist__desc">%s</span></a></li>' % (e(p["slug"]), e(p["baslik"]), e(meta), e(p["ozet"])))
    b += '<div class="wrap"><ul class="linklist">%s</ul></div>' % "".join(items)
    page("projeler.html", "Projeler", "Değerlendirilen projelerin listesi.", b, "projeler.html")


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


def p_proje(p, prev_p, next_p):
    b = head("Proje", p["baslik"], e(p["ozet"]))
    anchors = "".join('<a href="#%s">%s</a>' % (e(i), e(OPT[i]["tanim"]["ad"])) for i in p["secenekler"])
    b += '<div class="wrap"><nav class="anchor-nav" aria-label="Bu sayfadaki seçenekler">%s</nav></div>' % anchors
    bugun = p["bugun"]
    var = '<ul class="bullets">%s</ul>' % "".join("<li>%s</li>" % e(x) for x in bugun["var"])
    yok = '<ul class="bullets">%s</ul>' % "".join("<li>%s</li>" % e(x) for x in bugun["yok"])
    b += section("Bugün", '<div class="split"><div><h3>Var</h3><div class="mt-3">%s</div></div><div><h3>Henüz yok</h3><div class="mt-3">%s</div></div></div>'
                 '<p class="mt-5"><strong>Ödeyen müşteri: %s.</strong></p>' % (var, yok, num(bugun["odeyen_musteri"])), None, "bugun")
    ik = p["iki_calisma"]
    b += section("İki çalışma ne diyor", '<dl class="dl"><div><dt>Claude çalışması</dt><dd>%s</dd></div><div><dt>GPT çalışması</dt><dd>%s</dd></div><div><dt>Ayrıştıkları yer</dt><dd>%s</dd></div><div><dt>Birleşik hüküm</dt><dd>%s</dd></div>'
                 '<div class="dl__wide"><dt>Analist görüşü</dt><dd>%s</dd></div></dl>' % (e(ik["claude"]), e(ik["gpt"]), e(ik["ayrisma"]), e(ik["birlesik"]), e(p["analist_gorusu"])),
                 "Kaynak: Claude çalışmasından %d, GPT çalışmasından %d belge." % (p["kaynak"]["claude"], p["kaynak"]["gpt"]), "iki-calisma")
    for i in p["secenekler"]:
        o = OPT[i]; t = o["tanim"]; n = o["nitel"]
        s = '<div class="opt__tags mb-4">%s%s<span class="small muted">%s</span></div>' % (
            tag(o["karar"], o["karar_ad"]), gsum(o["kapi"]), e(("Yatırım sırası %d · öğrenme sırası %d" % (o["yatirim_sirasi"], o["ogrenme_sirasi"])) if "yatirim_sirasi" in o else "Sıralamaya girmiyor"))
        s += '<p class="prose">%s</p>' % e(KARAR_ACIKLAMA[o["karar"]])
        s += '<div class="split split--wide-first mt-5"><div><div class="score"><span class="score__num">%s</span><span class="score__den">/ 100 puan · kanıtla desteklenen %s · stratejik %s</span></div><div class="mt-3 mb-3">%s</div>%s</div>' % (
            num(n["puan"]), num(n["duzeltilmis"]), num(o["stratejik"]) if o["stratejik"] is not None else "–", meter(n["puan"], n["duzeltilmis"]), legend())
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
        s += '<h3 class="mt-6 mb-4">Altı aylık nakit</h3>%s' % finans_tablo(o)
        s += '<h3 class="mt-6 mb-4">Sıradaki deney</h3>%s' % deney_blok(o)
        ids = [c["id"] for c in M["kriterler"]]
        fk = o["fark"]
        uy = ("İki bağımsız değerlendirici arasındaki ortalama fark %s puan; kriterlerin %s'inde fark en çok 1." % (num(fk["ortalama"], 1), pct(fk["bir_icinde"]))) if fk["ortalama"] is not None else "Bu seçenekte tek değerlendirici puanı var."
        s += '<div class="mt-6"><details><summary>Kriter kriter puanlar (26)</summary><div class="details__body"><p class="small muted mb-3">%s</p>%s</div></details>' % (e(uy), crit_rows(o, ids))
        s += '<details><summary>Stratejik eksen (4)</summary><div class="details__body"><p class="small muted mb-3">Stratejik puan nakit puanıyla toplanmaz; uzun vadeli değeri ayrı gösterir.</p>%s</div></details>' % crit_rows(o, [c["id"] for c in M["stratejik"]])
        s += '<details><summary>Puanlamaya dayanak notlar</summary><div class="details__body"><p class="prose small">%s</p></div></details></div>' % e(t["kanit_notlari"])
        b += section(t["ad"], s, "%s · %s" % (e(t["tur"]), e(o["etiketler"]["segment"])), o["id"])
    hk = p.get("hakem") or []
    if hk:
        AD = {"kabul": "Kabul edildi", "kismen": "Kısmen kabul edildi", "ret": "Reddedildi"}
        say = {k: sum(1 for x in hk if x["karar"] == k) for k in AD}
        rows = "".join('<li class="ruling" data-karar="%s"><span>%s</span><span class="ruling__verdict">%s</span>%s<span class="ruling__why">%s</span></li>' % (
            x["karar"], e(x["itiraz"]), AD[x["karar"]], ('<span>Değişiklik: %s</span>' % e(x["degisiklik"])) if x.get("degisiklik") else "", e(x["gerekce"])) for x in hk)
        b += section("İtirazlar ve hakem kararları", '<details><summary>%d itiraz: %d kabul, %d kısmen, %d ret</summary><div class="details__body"><ul class="rulings">%s</ul></div></details>' % (
            len(hk), say["kabul"], say["kismen"], say["ret"], rows),
            "İkinci değerlendirici, karttaki tanım, kapı ve finans girdilerinden katılmadıklarını yazdı. Her itirazı ayrı bir hakem kaynak belgeye bakarak karara bağladı; kabul edilenler karta işlendi.", "itirazlar")
    pg = '<div class="wrap"><nav class="pager" aria-label="Projeler arası">'
    pg += ('<a class="pager__prev" href="%s.html"><small>Önceki proje</small>%s</a>' % (e(prev_p["slug"]), e(prev_p["baslik"]))) if prev_p else "<span></span>"
    pg += ('<a class="pager__next" href="%s.html"><small>Sonraki proje</small>%s</a>' % (e(next_p["slug"]), e(next_p["baslik"]))) if next_p else ""
    pg += "</nav></div>"
    page("proje/%s.html" % p["slug"], p["baslik"], p["ozet"], b + pg, "projeler.html", 1)


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
    pages_extra.build(D, yatirim, ogrenme, kalan, OPT)
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print("site üretildi:", OUT, "dosya:", n)


if __name__ == "__main__":
    main()
