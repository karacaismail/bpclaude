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
    ("sorular.html", "Tanı soruları"),
    ("duyarlilik.html", "Duyarlılık"),
    ("portfoy.html", "Portföy"),
    ("indir.html", "İndir"),
    ("hakkinda.html", "Hakkında"),
]

def _paper():
    """theme-color değerleri elle yazılmaz; tokens.css içindeki --c-paper değerlerinden okunur."""
    css = open(os.path.join(ROOT, "src", "styles", "tokens.css"), encoding="utf-8").read()
    vals = re.findall(r"--c-paper:\s*(#[0-9a-fA-F]{6})", css)
    return (vals[0], vals[1]) if len(vals) >= 2 else ("#ffffff", "#000000")


PAPER = _paper()

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
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def tl(v):
    if v is None: return "–"
    a = abs(v); neg = "−" if v < 0 else ""
    if a >= 1e6: return "%s₺%s mn" % (neg, num(a / 1e6, 2))
    if a >= 1e4: return "%s₺%s bin" % (neg, num(a / 1e3, 1 if a < 1e5 else 0))
    return "%s₺%s" % (neg, num(a))


def usd(v):
    if v is None: return "–"
    neg = "−" if v < 0 else ""
    return "%s%s USD" % (neg, num(abs(v)))


def pct(v, d=0):
    return "–" if v is None else "%%%s" % num(100 * v, d)


def page(path, title, desc, body, current=None, depth=0, absolute=False):
    rel = BASE_PATH if absolute else "../" * depth
    nav = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        nav.append('<li><a href="%s%s"%s>%s</a></li>' % (rel, href, cur, e(label)))
    doc = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="%(csp)s">
<title>%(title)s · %(site)s</title>
<meta name="description" content="%(desc)s">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="%(paper_l)s" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="%(paper_d)s" media="(prefers-color-scheme: dark)">
<link rel="stylesheet" href="%(rel)sassets/site.css">
<script src="%(rel)sassets/site.js" defer></script>
</head>
<body>
<a class="skip-link" href="#icerik">İçeriğe geç</a>
<header class="site-header">
<div class="wrap site-header__in">
<a class="brand" href="%(rel)sindex.html"><span class="brand__mark" aria-hidden="true"></span><span class="brand__name">%(site)s</span><span class="brand__sub">proje seçim defteri</span></a>
<a class="nav-toggle" href="#site-nav-list">Menü</a>
</div>
<nav class="site-nav" aria-label="Site"><ul id="site-nav-list" class="wrap site-nav__list">%(nav)s</ul></nav>
</header>
<main id="icerik">
%(body)s
</main>
<footer class="site-footer"><div class="wrap">
<p>%(site)s · %(tarih)s. Puanlar kaynak belgelerden çıkarılmış tahminlerdir; bir başarı olasılığı değildir. Hiçbir seçenekte ödeyen müşteri kanıtı yoktur.</p>
<p><a href="%(rel)shakkinda.html">Yöntem, kaynaklar ve sınırlar</a> · <a href="%(rel)sindir.html">Çalışma kitabını indir</a></p>
</div></footer>
</body>
</html>
""" % {"title": e(title), "site": SITE, "desc": e(desc), "rel": rel, "nav": "".join(nav), "body": body, "tarih": TARIH, "csp": CSP, "paper_l": PAPER[0], "paper_d": PAPER[1]}
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(doc)
    return full


def head(eyebrow, title, lede=None):
    s = '<div class="wrap page-head">'
    if eyebrow: s += '<p class="eyebrow">%s</p>' % e(eyebrow)
    s += "<h1>%s</h1>" % e(title)
    if lede: s += '<p class="lede">%s</p>' % lede
    return s + "</div>"


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


def meter(puan, duzeltilmis, label=None):
    lab = label or ("Puan %s / 100; kanıtla desteklenen kısım %s" % (num(puan), num(duzeltilmis)))
    return ('<div class="meter" role="img" aria-label="%s"><span class="meter__claim" style="--v:%.1f%%"></span>'
            '<span class="meter__proven" style="--p:%.1f%%"></span></div>') % (e(lab), max(0, min(100, puan)), max(0, min(100, duzeltilmis)))


def tag(karar, ad):
    return '<span class="tag" data-karar="%s">%s</span>' % (e(karar), e(ad))


def gsum(k):
    """Kapı özeti: işaret biçimle, anlam görünür metinle verilir (yalnız renge ya da biçime dayanmaz)."""
    return ('<span class="gsum"><span class="visually-hidden">Kapılar: </span><span class="gsum__part"><span class="dot dot--gecti" aria-hidden="true"></span>%d geçti</span>'
            '<span class="gsum__part"><span class="dot dot--test" aria-hidden="true"></span>%d test</span>'
            '<span class="gsum__part"><span class="dot dot--kaldi" aria-hidden="true"></span>%d kaldı</span></span>') % (k["gecti"], k["test"], k["kaldi"])


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
    facts = [
        ("6 ay net nakit", "%s<small>kötü %s</small><small>iyi %s</small>" % (tl(f["baz"]["net_nakit"]), tl(f["kotu"]["net_nakit"]), tl(f["iyi"]["net_nakit"]))),
        ("İlk tahsilat", "%s-%s gün<small>kalan efor %s saat</small>" % (num(fi["ilk_tahsilat_gun"]["min"]), num(fi["ilk_tahsilat_gun"]["max"]), num(fi["kalan_efor_saat"]["beklenen"]))),
        ("Kurucu saati", "%s saat<small>saat başı %s</small>%s" % (num(f["baz"]["kurucu_saat"]), tl(saat) if saat is not None else "–",
                                                                   "<small>kapasiteyi aşıyor</small>" if f.get("kapasite_asimi") else "")),
    ]
    fhtml = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), b) for a, b in facts)
    return ('<li class="opt" id="row-%(id)s" %(attrs)s>'
            '<div class="opt__rank"><span class="visually-hidden">Sıra </span>%(rank)s</div>'
            '<div class="opt__main"><h3 class="opt__title"><a href="%(rel)sproje/%(proje)s.html#%(id)s">%(ad)s</a></h3>'
            '<p class="opt__proj">%(pb)s · %(tur)s</p>%(ne)s'
            '<div class="opt__tags">%(tag)s%(gs)s</div></div>'
            '<div class="opt__score"><div class="score"><span class="score__num">%(p)s</span><span class="score__den">/ 100 puan</span></div>%(meter)s'
            '<p class="xs muted">kanıtla desteklenen %(adj)s · ortalama kanıt E%(kort)s</p></div>'
            '<dl class="opt__facts facts">%(facts)s</dl></li>') % {
        "id": e(o["id"]), "attrs": extra_attrs, "rank": e(rank), "rel": rel, "proje": e(o["proje"]), "ad": e(o["tanim"]["ad"]),
        "pb": e(o["proje_baslik"]), "tur": e(o["tanim"]["tur"]), "ne": ('<p class="opt__what">%s</p>' % e(ne)) if ne else "", "tag": tag(o["karar"], o["karar_ad"]), "gs": gsum(o["kapi"]),
        "p": num(n["puan"]), "meter": meter(n["puan"], n["duzeltilmis"]), "adj": num(n["duzeltilmis"]), "kort": num(n["kanit_ort"], 1), "facts": fhtml}


def minify_css(css):
    """Yorumları ve gereksiz boşlukları siler. ":" önündeki boşluk korunur: ".x :focus-visible" soy seçicisi bozulmasın."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    return css.replace(";}", "}").strip()
