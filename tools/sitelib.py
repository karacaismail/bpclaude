"""Site üretimi için yardımcılar: biçimlendirme, ortak iskelet, bileşen parçaları."""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
SITE = "bpclaude"
TARIH = "1 Ekim 2026"
# Yayın yolu: GitHub Pages proje sitesinde /bpclaude/. Yalnız 404 sayfası mutlak yol kullanır, çünkü her derinlikte sunulur.
BASE_PATH = os.environ.get("BPCLAUDE_BASE", "/bpclaude/")
# Site yalnız kendi kaynaklarını yükler; satır içi betik yoktur. Satır içi stil yalnız puan çubuğunun genişlik değişkenleri içindir.
CSP = ("default-src 'none'; style-src 'self'; style-src-elem 'self'; style-src-attr 'unsafe-inline'; script-src 'self'; img-src 'self'; font-src 'self'; "
       "connect-src 'none'; base-uri 'none'; form-action 'none'")

NAV = [
    ("index.html", "Özet"),
    ("siralama.html", "Sıralama"),
    ("projeler.html", "Projeler"),
    ("sablon.html", "Şablon"),
    ("sorular.html", "Sorular"),
    ("duyarlilik.html", "Duyarlılık"),
    ("portfoy.html", "Portföy"),
    ("indir.html", "İndir"),
    ("hakkinda.html", "Hakkında"),
]

def _cover():
    """theme-color değerleri elle yazılmaz; tokens.css içindeki --c-cover değerlerinden (açık ve koyu tema) okunur."""
    css = open(os.path.join(ROOT, "src", "styles", "tokens.css"), encoding="utf-8").read()
    vals = re.findall(r"--c-cover:\s*(#[0-9a-fA-F]{6})", css)
    return (vals[0], vals[1]) if len(vals) >= 2 else ("#000000", "#000000")


COVER = _cover()

KAPI_AD = {"gecti": "geçti", "test": "test", "kaldi": "kaldı"}
KARAR_ACIKLAMA = {
    "yatirim-yap": "Kapılar geçildi, ödeme kanıtı var ve baz senaryo hedefe ulaşıyor.",
    "once-test-et": "Uygunluk puanı tabanın üstünde ve baz senaryo altı ayda hedefin en az yarısını bırakıyor; ama kanıt zayıf. Büyük yatırımdan önce deney kartındaki test yapılır.",
    "degistir": "Bu biçimiyle iki koşuldan yalnız birini sağlıyor: ya uygunluk yeterli ama altı aylık nakit hedefin yarısına ulaşmıyor, ya da nakit hesabı iyi ama uygunluk zayıf. Müşteri, fiyat, kanal ya da kapsam değiştirilip yeniden puanlanır.",
    "beklet": "Kısa vadeli nakit için uygun değil, stratejik puanı yüksek; dondurulur ve yeniden değerlendirme tarihi konur.",
    "birak": "Uygunluk, altı aylık nakit ve stratejik puan birlikte düşük; kaynak ayrılmaz.",
    "kapida-kaldi": "En az bir kapı geçilemedi; puan ne olursa olsun sıralamaya girmez.",
}


def e(s):
    return html.escape(str(s), quote=True)


TR_FOLD = str.maketrans({"İ": "i", "I": "i", "ı": "i", "Ş": "s", "ş": "s", "Ğ": "g", "ğ": "g", "Ü": "u", "ü": "u", "Ö": "o", "ö": "o", "Ç": "c", "ç": "c",
                         "Â": "a", "â": "a", "Î": "i", "î": "i", "Û": "u", "û": "u"})


def tr_lower(s):
    """Türkçe küçük harf: İ→i, I→ı (Python'un lower() işlevi İ harfine birleşik nokta ekler)."""
    return str(s).replace("İ", "i").replace("I", "ı").lower()


def tr_capitalize(s):
    """Türkçe ilk harf büyütme: i→İ, ı→I."""
    s = str(s)
    if not s: return s
    first = {"i": "İ", "ı": "I"}.get(s[0], s[0].upper())
    return first + s[1:]


def fold(s):
    """Arama için sadeleştirme: Türkçe harfler temel harfe iner. src/site.js içindeki fold() ile aynı olmalı."""
    return str(s).translate(TR_FOLD).lower()


def num(v, d=0):
    """Türkçe sayı biçimi: binlik nokta, ondalık virgül."""
    if v is None: return "–"
    s = ("{:,.%df}" % d).format(v)
    return s.replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


def tl(v):
    if v is None: return "–"
    a = abs(v); neg = "−" if v < 0 else ""
    if a >= 1e6: return "%s₺%s mn" % (neg, num(a / 1e6, 2))
    if a >= 1e4: return "%s₺%s bin" % (neg, num(a / 1e3, 1 if a < 1e5 else 0))
    return "%s₺%s" % (neg, num(a))


def pct(v, d=0):
    return "–" if v is None else "%%%s" % num(100 * v, d)



def page(path, title, desc, body, current=None, depth=0, absolute=False, ust=False):
    """ust=True: sayfa, gezinmedeki bağlantının alt sayfasıdır (ör. proje sayfası); bağlantı "page" değil "true" ile işaretlenir."""
    rel = BASE_PATH if absolute else "../" * depth
    nav = []
    for href, label in NAV:
        cur = (' aria-current="%s"' % ("true" if ust else "page")) if href == current else ""
        nav.append('<li><a href="%s%s"%s>%s</a></li>' % (rel, href, cur, e(label)))
    # Alt gezinme şeritle aynı sayfaları ve aynı adları kullanır: şeritte kaydıramayan kullanıcının ikinci yoludur.
    foot = "".join('<li><a href="%s%s">%s</a></li>' % (rel, h, e(l)) for h, l in NAV)
    doc = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="%(csp)s">
<title>%(title)s · %(site)s</title>
<meta name="description" content="%(desc)s">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="%(cover_l)s" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="%(cover_d)s" media="(prefers-color-scheme: dark)">
<link rel="icon" href="%(rel)sassets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="%(rel)sassets/site.css">
<noscript><link rel="stylesheet" href="%(rel)sassets/noscript.css"></noscript>
<script src="%(rel)sassets/site.js" defer></script>
</head>
<body>
<header class="site-header on-cover">
<a class="skip-link" href="#icerik">İçeriğe geç</a>
<div class="wrap site-header__in">
<a class="brand" href="%(rel)sindex.html"><span class="brand__mark" aria-hidden="true"></span><span class="brand__name">%(site)s</span></a>
<nav class="site-nav" aria-label="Site"><ul id="site-nav-list" class="site-nav__list">%(nav)s</ul></nav>
</div>
</header>
<main id="icerik">
%(body)s
</main>
<footer class="site-footer on-cover"><div class="wrap site-footer__in">
<div><p class="brand"><span class="brand__mark" aria-hidden="true"></span><span class="brand__name">%(site)s</span></p>
<p class="site-footer__note">%(tarih)s. Puanlar kaynak belgelerden çıkarılmış tahminlerdir; bir başarı olasılığı değildir. Hiçbir seçenekte ödeyen müşteri kanıtı yoktur.</p></div>
<nav aria-label="Alt bölüm"><ul class="footer-nav">%(foot)s</ul></nav>
</div></footer>
</body>
</html>
""" % {"title": e(title), "site": SITE, "desc": e(desc), "rel": rel, "nav": "".join(nav), "foot": foot, "body": body, "tarih": TARIH, "csp": CSP,
       "cover_l": COVER[0], "cover_d": COVER[1]}
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(doc)
    return full


def head(eyebrow, title, lede=None, fig=None):
    """Sayfa başı bandı. fig verilirse başlığın yanına (dar ekranda altına) sayfanın özet grafiği yerleşir."""
    s = '<div class="masthead"><div class="wrap page-head%s"><div>' % (" page-head--fig" if fig else "")
    if eyebrow: s += '<p class="eyebrow">%s</p>' % e(eyebrow)
    s += "<h1>%s</h1>" % e(title)
    if lede: s += '<p class="lede">%s</p>' % lede
    s += "</div>"
    if fig: s += '<div class="page-head__fig">%s</div>' % fig
    return s + "</div></div>"


def split_title(baslik):
    """'qral (hızlı başvuru …)' biçimindeki başlığı ad ve açıklama olarak ayırır."""
    b = str(baslik).strip()
    if b.endswith(")") and " (" in b:
        i = b.index(" (")
        return b[:i], b[i + 2:-1]
    return b, None


def section(title, inner, intro=None, sid=None, tag="h2", kicker=None, band=False):
    ida = ' id="%s"' % sid if sid else ""
    s = '<section class="section%s"%s><div class="wrap">' % (" section--band" if band else "", ida)
    s += '<div class="section__head">'
    if kicker: s += '<p class="section__kicker">%s</p>' % e(kicker)
    s += '<%s>%s</%s>' % (tag, e(title), tag)
    if intro: s += "<p>%s</p>" % intro
    s += "</div>" + inner + "</div></section>"
    return s


def meter(puan, duzeltilmis, label=None, gizli=False):
    """Puan çubuğu. gizli=True: aynı sayılar bitişik metinde yazıyorsa grafik yardımcı teknolojiden gizlenir (yineleme olmasın)."""
    lab = label or ("Puan %s / 100; kanıtla desteklenen kısım %s" % (num(puan), num(duzeltilmis)))
    return ('<div class="meter" %s><span class="meter__claim" style="--v:%.1f%%"></span>'
            '<span class="meter__proven" style="--p:%.1f%%"></span></div>') % (
        'aria-hidden="true"' if gizli else 'role="img" aria-label="%s"' % e(lab), max(0, min(100, puan)), max(0, min(100, duzeltilmis)))


def tag(karar, ad):
    return '<span class="tag" data-karar="%s">%s</span>' % (e(karar), e(ad))


def gsum(k, kapilar=None, kisa=False, onek=True):
    """Kapı özeti. Sekiz nokta kapıları sırasıyla gösterir (biçim durumu ayırır: dolu daire geçti, yarım daire test, içi boş kare kaldı).
    Liste satırında görünür metin kısadır (geçen / toplam); tam döküm ekran okuyucuya verilir. Proje sayfasında tam döküm görünür.
    onek=False: "Kapılar" adı bitişik görünür etikette zaten yazıyorsa gizli önek yinelenmez."""
    dots = ""
    if kapilar:
        dots = '<span class="gates8" aria-hidden="true">%s</span>' % "".join(
            '<span class="dot dot--%s"></span>' % v["durum"] for g, v in sorted(kapilar.items()))
    if kisa:
        return ('<span class="gsum"><span class="visually-hidden">Kapılar: %d geçti, %d test, %d kaldı.</span>%s'
                '<span class="gsum__text" aria-hidden="true">%d/%d geçti</span></span>') % (
            k["gecti"], k["test"], k["kaldi"], dots, k["gecti"], k["gecti"] + k["test"] + k["kaldi"])
    return ('<span class="gsum">%s%s<span class="gsum__text">%d geçti · %d test · %d kaldı</span></span>') % (
        '<span class="visually-hidden">Kapılar: </span>' if onek else "", dots, k["gecti"], k["test"], k["kaldi"])


RANGE_LO, RANGE_HI = -0.5, 1.5   # hedefin katı olarak eksen sınırları: sıfır yüzde 25'te, hedef yüzde 75'te durur


# Tarama kırıntısı kuralı (yüzde, çizgi genişliğine göre). Nokta ve halesi yaklaşık 16 px tutar; en dar sütunda (yaklaşık 200 px)
# bu, noktanın iki yanında yüzde 4,5 eder. Noktanın bir yanında bundan sonra kalan tarama yüzde 5'ten kısaysa o yan çizilmez
# (tarama noktanın merkezinden başlar); iki yan da kısaysa tarama hiç çizilmez. Uç değerler zaten metinde yazılıdır.
# tests/kabul.spec.js içindeki denetim aynı iki sayıyı kullanır.
RANGE_HALE = 4.5
RANGE_KIRINTI = 5.0


def range_plot(f, eksen=False):
    """Altı aylık net nakit: kötü-iyi aralığı (taralı: varsayım), baz senaryo noktası (artı: dolu, eksi: içi boş), sıfır ve hedef çentiği.
    Ölçek doğrusaldır. Aralık ölçeği aşarsa o uca ok konur; baz değerin kendisi ölçek dışındaysa nokta çizilmez, yalnız ok kalır.
    Noktanın yanında kırıntı kadar kalan tarama çizilmez (RANGE_HALE ve RANGE_KIRINTI).
    eksen=True çentiklerin altına "0" ve "hedef" yazar.
    Grafik yardımcı teknolojiden gizlidir: aynı değerler her kullanımda bitişik metinde ya da tabloda yazılıdır."""
    h = float(f["hedef_tl"])
    def raw(v):
        return (v / h - RANGE_LO) / (RANGE_HI - RANGE_LO)
    def pos(v):
        return max(0.0, min(1.0, raw(v))) * 100.0
    k, b, i = f["kotu"]["net_nakit"], f["baz"]["net_nakit"], f["iyi"]["net_nakit"]
    lo, hi = min(k, b, i), max(k, b, i)
    a, z = pos(lo), pos(hi)
    tasma = " ".join(ad for ad, var in (("sol", raw(lo) < 0), ("sag", raw(hi) > 1)) if var)
    disarida = raw(b) < 0 or raw(b) > 1
    bp = pos(b)
    if not disarida:
        if "sol" not in tasma and (bp - RANGE_HALE) - a < RANGE_KIRINTI: a = bp
        if "sag" not in tasma and z - (bp + RANGE_HALE) < RANGE_KIRINTI: z = bp
    # Taşma oku taramanın uç parçasıdır: ölçeği aşan satırda tarama sıfır genişlikte de olsa durur.
    tarama = '<span class="range__span"></span>' if (tasma or z - a > 0) else ""
    nokta = "" if disarida else '<span class="range__dot"></span>'
    s = ('<div class="range" aria-hidden="true" data-isaret="%s"%s style="--a:%.1f%%;--w:%.1f%%;--b:%.1f%%;--z:%.1f%%;--t:%.1f%%">'
         '%s<span class="range__zero"></span><span class="range__target"></span>%s</div>') % (
        "eksi" if b <= 0 else "arti", (' data-tasma="%s"' % tasma) if tasma else "", a, z - a, bp, pos(0), pos(h), tarama, nokta)
    if eksen:
        s += '<span class="range__axis" aria-hidden="true" style="--z:%.1f%%;--t:%.1f%%"><span>0</span><span>hedef %s</span></span>' % (pos(0), pos(h), tl(h))
    return s


def metric_score(n):
    """Uygunluk puanı ölçüsü: değer, kanıtla desteklenen kısım ve puan çubuğu. Liste satırı ile proje başı aynı bileşeni kullanır."""
    return ('<div class="metric metric--score"><span class="metric__label">Uygunluk</span> '
            '<span class="metric__val"><b>%s</b> / 100 <span class="metric__note">· kanıtlı %s</span></span>%s</div>') % (
        num(n["puan"]), num(n["duzeltilmis"]), meter(n["puan"], n["duzeltilmis"], gizli=True))


def metric_cash(f, eksen=False):
    """Altı ay net nakit ölçüsü: baz değer, aralık çizgisi ve çizginin iki ucundaki kötü ve iyi senaryo."""
    hedef = ('<span class="visually-hidden"> Hedef %s.</span>' % tl(f["hedef_tl"])) if eksen else ""
    return ('<div class="metric metric--cash"><span class="metric__label">6 ay net nakit</span> <span class="metric__val"><b>%s</b></span>%s'
            '<span class="metric__sub metric__sub--ends"><span>kötü\u00a0%s</span> <span>iyi\u00a0%s</span></span>%s</div>') % (
        tl(f["baz"]["net_nakit"]), range_plot(f, eksen), tl(f["kotu"]["net_nakit"]), tl(f["iyi"]["net_nakit"]), hedef)


def pips(p):
    if p is None:
        return '<span class="muted">bilinmiyor</span>'
    cells = "".join('<span class="pip%s"></span>' % (" is-on" if i < p else "") for i in range(5))
    return '<span class="pips" aria-hidden="true">%s</span><span>%d/5</span>' % (cells, p)


def ev_legend(depth=0):
    """E0-E4 kodlarının görünür açıklaması; ayrıntı şablon sayfasında."""
    rel = "../" * depth
    return ('<p class="ev-legend small"><span>Kanıt kodu:</span> <span class="ev" data-k="0">E0</span> varsayım · <span class="ev" data-k="1">E1</span> dış kaynak ya da beyan · '
            '<span class="ev" data-k="2">E2</span> davranış · <span class="ev" data-k="3">E3</span> ödeme · <span class="ev" data-k="4">E4</span> tekrarlanan ödeme. '
            '<a href="%ssablon.html#kanit">Kanıt ölçeği</a></p>') % rel


def ev(k, olcek):
    return '<span class="ev" data-k="%d" title="%s">E%d</span>' % (k, e(olcek[k]["tanim"]), k)


def opt_row(o, rank, depth=0, extra_attrs="", ne=None):
    rel = "../" * depth
    n = o["nitel"]; f = o["finans"]; fi = o["finans_girdi"]
    saat = f["baz"]["saat_basi"]
    duz = ('<div class="metric metric--plain"><span class="metric__label">İlk\u00a0tahsilat</span> <span class="metric__val"><b>%s-%s\u00a0gün</b></span> '
           '<span class="metric__sub">kalan\u00a0efor\u00a0%s\u00a0saat</span></div>'
           '<div class="metric metric--plain"><span class="metric__label">Kurucu\u00a0saati</span> <span class="metric__val"><b>%s\u00a0saat</b></span> '
           '<span class="metric__sub">saat\u00a0başı\u00a0%s</span>%s</div>') % (
        num(fi["ilk_tahsilat_gun"]["min"]), num(fi["ilk_tahsilat_gun"]["max"]), num(fi["kalan_efor_saat"]["beklenen"]),
        num(f["baz"]["kurucu_saat"]), tl(saat) if saat is not None else "–", ' <span class="metric__sub">kapasiteyi\u00a0aşıyor</span>' if f.get("kapasite_asimi") else "")
    return ('<li class="opt" id="row-%(id)s" %(attrs)s>'
            '<div class="opt__rank"><span class="visually-hidden">Sıra </span>%(rank)s</div>'
            '<div class="opt__main"><h3 class="opt__title"><a href="%(rel)sproje/%(proje)s.html#%(id)s">%(ad)s</a></h3>'
            '<p class="opt__proj">%(pb)s\u00a0· %(tur)s</p>%(ne)s'
            '<div class="opt__tags">%(tag)s%(gs)s</div></div>'
            '<div class="opt__metrics">%(score)s%(cash)s%(duz)s</div></li>') % {
        "id": e(o["id"]), "attrs": extra_attrs, "rank": e(rank), "rel": rel, "proje": e(o["proje"]), "ad": e(o["tanim"]["ad"]),
        "pb": e(o["proje_baslik"]), "tur": e(o["tanim"]["tur"]), "ne": ('<p class="opt__what">%s</p>' % e(ne)) if ne else "", "tag": tag(o["karar"], o["karar_ad"]),
        "gs": gsum(o["kapi"], o["kapilar"], kisa=True), "score": metric_score(n), "cash": metric_cash(f), "duz": duz}


def legend(nakit=True):
    """İşaretlerin açıklaması, üç grupta: puan çubuğu (dolu: kanıt, taralı: varsayım), kapı noktaları ve nakit aralığı çizgisi."""
    sw = lambda cls: '<span class="%s" aria-hidden="true"></span>' % cls
    gruplar = [("Puan", [(sw("legend__swatch"), "kanıtla desteklenen"), (sw("legend__swatch legend__swatch--claim"), "varsayım")]),
               ("Kapı", [(sw("dot dot--gecti"), "geçti"), (sw("dot dot--test"), "test"), (sw("dot dot--kaldi"), "kaldı")])]
    if nakit:
        gruplar.append(("Nakit", [(sw("i-dot"), "baz artı"), (sw("i-dot i-dot--eksi"), "baz eksi"), (sw("legend__swatch legend__swatch--claim"), "kötü ile iyi arası"),
                                  (sw("i-zero"), "sıfır"), (sw("i-target"), "hedef"), (sw("i-arrow"), "ölçek dışına taşıyor")]))
    return '<div class="legend">%s</div>' % "".join(
        '<p class="legend__group"><strong>%s</strong>%s</p>' % (e(ad), "".join('<span class="legend__item">%s%s</span>' % (ikon, e(t)) for ikon, t in oge)) for ad, oge in gruplar)


def howto(giris=None, not_=None):
    """Liste başındaki kapalı "işaretler" bölümü: listeye yer açmak için gösterge açılır bölümde durur.
    giris göstergeden önce, not_ (ör. hedef tutarı ve ölçek) göstergeden sonra yazılır."""
    return '<details class="howto"><summary>İşaretler nasıl okunur</summary><div class="details__body">%s%s%s</div></details>' % (
        ('<p class="small mb-3">%s</p>' % e(giris)) if giris else "", legend(), ('<p class="small mt-3">%s</p>' % e(not_)) if not_ else "")


KATMANLAR = [("kapilar", "Kapılar", "Sekiz koşul; biri kaldıysa seçenek sıralamaya girmez."), ("kriterler", "Puan", "26 kriter, altı kategori; her biri 0 ile 5 arasında."),
             ("kanit", "Kanıt", "Her puanın yanında E0-E4 kanıt düzeyi."), ("nakit", "Nakit", "Altı aylık net nakit; puanla toplanmaz."),
             ("stratejik", "Strateji", "Uzun vadeli değer ayrı eksende.")]


def layers_html(prefix=""):
    """Şablonun beş katmanı: numaralı adım bağlantıları."""
    return '<ol class="layers">%s</ol>' % "".join(
        '<li><a href="%s#%s"><span><span class="layers__name">%s</span> <span class="layers__desc">%s</span></span></a></li>' % (prefix, a, e(n), e(d)) for a, n, d in KATMANLAR)


def minify_js(js):
    """Yorum satırlarını, satır başı girintisini ve boş satırları siler; kodun kendisine dokunmaz (satır sonları korunur).
    Kaynak dosya (src/site.js) yorumlarıyla okunur kalır; yayımlanan dosya küçülür.
    Sınır: satır tabanlıdır. Kaynakta çok satırlı şablon dizgisi ya da satırı "//" ile başlayan dizgi içeriği kullanılmaz;
    kullanılırsa bu işlev onu sessizce bozar."""
    out = []
    for line in js.splitlines():
        t = line.strip()
        if not t or t.startswith("//"): continue
        out.append(t)
    return "\n".join(out) + "\n"


def minify_css(css):
    """Yorumları ve gereksiz boşlukları siler. ":" önündeki boşluk korunur: ".x :focus-visible" soy seçicisi bozulmasın."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    # Çarpma ve bölme işaretinin çevresindeki boşluk gereksizdir (toplama ve çıkarmanınki gereklidir, dokunulmaz);
    # "1 / -1" gibi ızgara değerleri ve "> * + *" gibi seçiciler boşluksuz da geçerlidir.
    css = re.sub(r" ?([*/]) ?", r"\1", css)
    # Sınır: bu iki kural dizgi ve url() içine de uygulanır ve ".x *" soy seçicisini ".x*" yapar; stil dosyalarında
    # içinde " / ", " * " ya da "0." geçen dizgi, url() ve boşlukla yazılmış "*" soy seçicisi kullanılmaz ("> *" güvenlidir).
    # Baştaki sıfır: 0.625rem → .625rem
    css = re.sub(r"(?<![\d.])0\.(\d)", r".\1", css)
    return css.replace(";}", "}").strip()
