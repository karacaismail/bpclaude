"""Şablon, tanı soruları, duyarlılık, portföy, indirme ve hakkında sayfaları."""
import csv, json, os
from sitelib import *  # noqa: F401,F403


def p_sablon(D):
    M = D["kriterler"]; H = D["hedef"]
    b = head("Şablon", "Seçim şablonu", "Projeleri değil ticari seçenekleri karşılaştıran, önce kapıdan geçiren, sonra puanlayan, parayı ayrıca hesaplayan ve her puanın yanına kanıtını yazan beş katmanlı bir yöntem.")
    b += '<div class="wrap"><nav class="anchor-nav" aria-label="Bu sayfada"><a href="#birim">Değerlendirme birimi</a><a href="#hedef">Hedef</a><a href="#kapilar">Kapılar</a><a href="#kriterler">Kriterler</a><a href="#kanit">Kanıt</a><a href="#nakit">Nakit hesabı</a><a href="#stratejik">Stratejik eksen</a><a href="#karar">Karar kuralları</a><a href="#deney">Deney kartı</a><a href="#kaynak">Üç kaynak</a></nav></div>'
    birim = ('<div class="prose"><p>Aynı kod üç farklı işe dönüşebilir: küçük işletmeye aylık abonelik, ajansa paket, tek bir kuruma kurulumlu proje. Müşteri bulma, fiyat, satış süresi ve destek yükü üçünde de farklıdır. Bu yüzden puanlanan şey proje değil, şu birleşimdir:</p>'
             '<p><strong>proje × müşteri × müşterinin işi × tetikleyici × teklif ve fiyat × dağıtım kanalı × ilk satılabilir kapsam</strong></p>'
             '<p>Bir projenin en çok üç seçeneği yazıldı. En az biri, kurucunun tek başına sekiz hafta içinde satabileceği en küçük kapsamdır.</p></div>')
    b += section("Değerlendirme birimi: ticari seçenek", birim, None, "birim")
    rows = [("Hedef", "%s; %s USD" % (H["tanim"], num(H["hedef_usd"]))), ("Süre", "%d ay" % H["ufuk_ay"]), ("Kur", "%s ₺ / USD" % num(H["kur_tl_usd"])),
            ("Haftalık kurucu saati", "%d saat" % H["haftalik_kurucu_saati"]), ("Eşik saat ücreti", "%s; aynı saatte danışmanlık yapmanın getirisi" % tl(H["esik_saat_ucreti_tl"])),
            ("Riske edilen nakit tavanı", tl(H["azami_riske_edilen_nakit_tl"])), ("Aynı anda yürütülen iş", "%d" % H["wip_siniri"])]
    b += section("Hedef ve kısıtlar", '<dl class="dl">%s</dl><p class="small muted mt-4">%s</p>' % ("".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), e(c)) for a, c in rows), e(H["not"])),
                 "Hedef yazılmadan ağırlıkların anlamı yoktur: altı ayda toplam nakit ile altıncı ayda aylık düzenli gelir farklı projeleri öne çıkarır. Bu çalışma toplam net nakdi esas aldı.", "hedef")
    gl = "".join('<details><summary>%s %s</summary><div class="details__body"><p>%s</p><dl class="dl mt-4"><div><dt>Geçti</dt><dd>%s</dd></div><div><dt>Test</dt><dd>%s</dd></div><div class="dl__wide"><dt>Kaldı</dt><dd>%s</dd></div></dl></div></details>' % (
        g["id"], e(g["ad"]), e(g["soru"]), e(g["gecti"]), e(g["test"]), e(g["kaldi"])) for g in M["kapilar"])
    b += section("Katman 1: kapılar", gl, "Kapıların ağırlığı yoktur; geçilir ya da geçilmez. Toplamaya dayalı puan, ölümcül bir eksiği başka kriterlerdeki yüksek puanla gizler; kapı bunu engeller. Bilinmeyen koşul sıfır puan almaz, test olarak işaretlenir.", "kapilar")
    kl = ""
    for k in M["kategoriler"]:
        cr = [c for c in M["kriterler"] if c["kat"] == k["id"]]
        inner = "".join('<li class="crit crit--tanim"><span class="crit__id">%s</span><span class="crit__name">%s<br><span class="muted small">ağırlık %s%s</span></span><span class="crit__why">%s<br><strong>1</strong> %s<br><strong>3</strong> %s<br><strong>5</strong> %s<br><span class="muted">Kanıt: %s</span></span></li>' % (
            c["id"], e(c["ad"]), num(c["agirlik"]), " · ters yönlü" if c["yon"] == "ters" else "", e(c["soru"]), e(c["c1"]), e(c["c3"]), e(c["c5"]), e(c["kanit"])) for c in cr)
        kl += '<details><summary><span>%s. %s <span class="summary__meta">ağırlık %s · %d kriter</span></span></summary><div class="details__body"><p class="prose">%s</p><ol class="crits mt-3">%s</ol></div></details>' % (
            k["id"], e(k["ad"]), num(k["agirlik"]), len(cr), e(k["soru"]), inner)
    olcek = "".join("<li><strong>%d</strong> %s</li>" % (x["puan"], e(x["anlam"])) for x in M["puan_olcegi"])
    b += section("Katman 2: 26 kriter, altı kategori", kl + '<div class="prose mt-5"><p>Puan ölçeği 0-5 arasıdır; 1, 3 ve 5 her kriter için gözlemlenebilir bir duruma bağlanmıştır.</p><ul>%s</ul>'
                 '<p>Kategori ağırlığı kriterlere dağıtılır; kategoriye ayrıca ek puan verilmez, çünkü aynı üstünlük iki kez sayılmış olur. Ters yönlü kriterlerde yük ya da risk azaldıkça puan artar. Dayanağı hiç olmayan kriter boş bırakılır; boş kriter sıfır sayılmaz, kalanlar da yüze tamamlanmaz. Sayfalarda kapsam ayrıca gösterilir.</p></div>' % olcek,
                 "Yüzlerce kriter yerine birbirinden bağımsız 26 kriter. Geri kalan sorular puanlanmayan bir kütüphaneye taşındı.", "kriterler")
    kt = "".join("<tr><th scope=\"row\">E%d</th><td>%s</td><td class=\"num\">%s</td></tr>" % (x["kod"], e(x["tanim"]), num(x["guven"], 1)) for x in M["kanit_olcegi"])
    b += section("Kanıt ölçeği", '<div class="table-wrap" tabindex="0" role="region" aria-label="Kanıt ölçeği"><table class="tbl"><thead><tr><th scope="col">Kod</th><th scope="col">Anlam</th><th scope="col" class="num">Güven katsayısı</th></tr></thead><tbody>%s</tbody></table></div>'
                 '<div class="prose mt-5"><p>Puan, seçeneğin ne kadar iyi göründüğünü; kanıt, bunu ne kadar bildiğimizi söyler. İkisi ayrı tutulur ve yan yana gösterilir: yüksek puan ve düşük kanıt, orta puan ve yüksek kanıtla aynı şey değildir.</p>'
                 '<p>Sıralamada kullanılan düzeltilmiş puan, her kriterin katkısının güven katsayısıyla çarpılmış toplamıdır. Çubukta dolu kısım düzeltilmiş puanı, taralı kısım varsayıma dayanan farkı gösterir.</p></div>' % kt,
                 "Görüşle verilen 5 ile ödemeyle kanıtlanmış 5 aynı değildir.", "kanit")
    nak = ('<div class="prose"><p>Puan parayı göstermez; nakit ayrı hesaplanır ve puanla toplanmaz. Her seçenek için kötü, baz ve iyi senaryo yazılır; senaryolara olasılık atanmaz.</p><ul>'
           '<li><strong>Altı aylık net nakit</strong> = tahsilat − ödeme adedi × değişken maliyet − 6 × aylık sabit gider − başlangıç harcaması.</li>'
           '<li><strong>Kurucu saati</strong> = ilk satılabilir kapsama kalan efor + müşteri sayısı × satış başına saat + ödeme adedi × (ödeme başına teslim saati + aylık destek dakikası ÷ 60). Teslim saati, hizmetlerde işin kendisini yapmak için harcanan emektir; kopyası satılan üründe sıfırdır. Kalan efor kötü senaryoda en yüksek, iyi senaryoda en düşük tahminle alınır.</li>'
           '<li><strong>Kapasite</strong> = haftalık kurucu saati × altı ay (%s saat). Baz senaryosu bundan çok saat isteyen seçenek o nakdi teslim edemez; nakit koşulunu sağlamış sayılmaz.</li>'
           '<li><strong>Saat başı nakit</strong> = net nakit ÷ kurucu saati. Eşik saat ücretinin altındaysa aynı saatlerde danışmanlık yapmak daha çok para bırakır; seçenek ancak stratejik gerekçeyle sürdürülür.</li>'
           '<li><strong>Hedef için gereken müşteri</strong> = (hedef + sabit giderler) ÷ müşteri başına katkı. <strong>Gereken nitelikli aday</strong> = gereken müşteri ÷ dönüşüm oranı.</li>'
           '<li><strong>Riske edilen nakit</strong> = başlangıç harcaması + ilk tahsilata kadar geçen sürenin sabit gideri.</li>'
           '</ul><p>Reklam harcaması sıfır olsa da müşteri edinmenin bedeli sıfır değildir; bu hesapta bedel kurucu saati olarak görünür. Geçmişte harcanan emek hesaba girmez, yalnız kalan efor girer.</p></div>') % num(H["haftalik_kurucu_saati"] * H["ufuk_ay"] * 52 / 12.0)
    b += section("Katman 3: altı aylık nakit", nak, None, "nakit")
    sl = "".join('<li class="crit crit--tanim"><span class="crit__id">%s</span><span class="crit__name">%s</span><span class="crit__why">%s<br><strong>1</strong> %s<br><strong>3</strong> %s<br><strong>5</strong> %s</span></li>' % (c["id"], e(c["ad"]), e(c["soru"]), e(c["c1"]), e(c["c3"]), e(c["c5"])) for c in M["stratejik"])
    b += section("Stratejik eksen", '<ol class="crits">%s</ol>' % sl, "Kısa vadeli nakit ile uzun vadeli değer tek sayıda birleştirilmez. Dört kriterlik stratejik puan ayrı hesaplanır ve yalnız bekletme kararında kullanılır.", "stratejik")
    ES = M["karar_esikleri"]
    yari = tl(H["hedef_usd"] * H["kur_tl_usd"] * ES["nakit_alt_orani"])
    kr = [("Yatırım yap", "Bütün kapılar geçti, uygunluk puanı en az %d, ödeme isteği kanıtı en az E%d ve baz senaryo hedefe ulaşıyor." % (ES["uygunluk_alt_puan"], ES["yatirim_kanit_kodu"])),
          ("Önce test et", "Kapıda kalmadı, uygunluk puanı en az %d, baz senaryoda altı aylık net nakit hedefin en az yarısı (%s) ve bu senaryo kurucunun altı aylık kapasitesine sığıyor. Büyük geliştirme bütçesi açılmaz; deney kartındaki test yapılır." % (ES["uygunluk_alt_puan"], yari)),
          ("Değiştir", "İki koşuldan yalnız biri sağlanıyor: uygunluk yeterli ama nakit hedefin yarısının altında ya da kapasiteyi aşıyor; ya da nakit yeterli ama uygunluk %d'in altında. Müşteri, fiyat, kanal ya da kapsam değiştirilip yeniden puanlanır." % ES["uygunluk_alt_puan"]),
          ("Beklet", "İki koşul da sağlanmıyor ama stratejik puan en az %d. Dondurulur; yeniden değerlendirme tarihi yazılır." % ES["stratejik_beklet_puan"]),
          ("Bırak", "İki koşul da sağlanmıyor ve stratejik puan %d'ın altında." % ES["stratejik_beklet_puan"]),
          ("Kapıda kaldı", "En az bir kapı geçilemedi. Sıralamaya girmez; kapının nasıl geçileceği seçenek sayfasında yazar.")]
    b += section("Karar kuralları", '<dl class="dl">%s</dl><div class="prose mt-5"><p><strong>Yatırım sırası</strong> önce karar sınıfına, sonra kanıtla düzeltilmiş puana göredir. Nakit koşulu bir kapı gibi çalışır: altı ayda hedefin yarısını bırakamayan seçenek, puanı ne olursa olsun kısa listeye girmez. <strong>Öğrenme sırası</strong> ayrı tutulur: puan × (1 − kanıtla desteklenen pay) ÷ deney saati. Puanı yüksek, kanıtı zayıf ve testi ucuz olan seçenek önce sınanır.</p><p>%s</p></div>' % (
        "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), e(c)) for a, c in kr), e(ES["not"])), "En yüksek puanlı seçenek otomatik olarak yatırım almaz. Karar, kapı sonucuna, puana, kanıta ve nakit hesabına birlikte bakar.", "karar")
    dn = [("Varsayım", "Kararı en çok değiştirecek, kanıtı en zayıf varsayım."), ("Yöntem", "Gerçek davranış üreten en ucuz test: fiyatlı teklif, ücretli pilot, ön satış, elle teslim."),
          ("Süre ve bütçe", "Gün, kurucu saati ve nakit; önceden sınırlanır."), ("Başarı ölçütü", "Test başlamadan yazılır; sonuç geldikten sonra değiştirilmez."),
          ("Bırakma ölçütü", "Hangi sonuçta bu seçeneğe saat ayırmanın bırakılacağı."), ("Sonraki dilim", "Test başarılıysa açılacak bir sonraki yatırım dilimi; hepsi değil.")]
    b += section("Deney kartı", '<dl class="dl">%s</dl>' % "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), e(c)) for a, c in dn),
                 "Tablo kurucunun bildiğini düzenler, bilmediğini öğretmez. Kısa listedeki her seçeneğin bir deney kartı vardır; karar deneyden gelen kanıtla verilir.", "deney")
    src = [("Claude araştırması", "Beş eleme kapısı, davranışla çapalanmış 1-3-5 ölçeği, kanıt düzeyine göre güven katsayısı, kalan efor ve ilk gelire kadar süre kriterleri, eşik saat ücreti, aynı anda tek iş sınırı, bırakma ölçütü, Türkiye'den tahsilat kısıtı."),
           ("ChatGPT araştırması", "Ticari seçenek birimi, geçti-test-kaldı kapıları, puan ile kanıtın ayrı gösterilmesi, altı aylık nakit ve gereken aday hesabı, kötü-baz-iyi senaryo, yatırım sırası ile öğrenme sırasının ayrılması."),
           ("Sohbet yanıtı", "Altı kategorili ağırlık dağılımı, kategoriye ek puan verilmemesi, bilinmeyenin sıfır sayılmaması, karşılaştırmaya hiçbir şey yapmama seçeneğinin eklenmesi, birlikte yürütülebilirlik kontrolü.")]
    fark = ["Kanıt puanla çarpılsın mı: bir kaynak evet, diğeri hayır diyor. İkisi de gösterildi: ham puan ve kanıt ayrı, sıralama düzeltilmiş puanla.",
            "Kriter sayısı: bir kaynak 8-15, diğeri 31 öneriyor. Birbirini tekrar eden kriterler birleştirildi, 26'da duruldu.",
            "Süre ve kalan efor: bir kaynakta kapı, diğerinde puan. İkisi de var: sekiz haftayı aşan seçenek kapıda kalır, altındakiler süreye göre puanlanır.",
            "Operasyon yükü: bir kaynak puana katmıyor, saat olarak izliyor. Burada hem düşük ağırlıklı bir kategori hem de kurucu saati hesabı var."]
    b += section("Üç kaynaktan ne alındı", '<dl class="dl">%s</dl><h3 class="mt-6 mb-3">Kaynakların ayrıştığı yerler</h3><ul class="bullets prose">%s</ul>' % (
        "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (e(a), e(c)) for a, c in src), "".join("<li>%s</li>" % e(x) for x in fark)),
        "Şablon, aynı soruya verilmiş üç yanıtın ortak noktalarından kuruldu. Ağırlıklar başlangıç önerisidir; Duyarlılık sayfası sıralamanın ağırlık seçimine ne kadar bağlı olduğunu gösterir.", "kaynak")
    page("sablon.html", "Şablon", "Kapılar, 26 kriter, kanıt ölçeği, nakit hesabı ve karar kuralları.", b, "sablon.html")


def p_sorular(D):
    S = json.load(open(os.path.join(ROOT, "model", "sorular.json"), encoding="utf-8"))
    total = sum(len(g["sorular"]) for g in S["gruplar"])
    b = head("Kütüphane", "Tanı soruları", "%d soru. Puanlanmaz; bir kriteri puanlamadan önce düşünmeyi derinleştirmek ve kör noktaları taramak içindir." % total)
    b += '<div class="wrap"><p class="prose">%s Yüzlerce kriterli bir tablo fikrinin doğru yeri burasıdır: kapsamlılık soru kütüphanesinde, ayırt edicilik 26 kriterlik karar modelinde.</p></div>' % e(S["not"])
    for g in S["gruplar"]:
        items = "".join('<li class="crit"><span class="crit__id">%s</span><span class="crit__name crit__name--wide">%s</span></li>' % (e(cid), e(q)) for cid, q in g["sorular"])
        b += section("%s (%d)" % (g["ad"], len(g["sorular"])), '<ol class="crits">%s</ol>' % items, None, "s-" + g["id"].lower())
    page("sorular.html", "Tanı soruları", "Puanlanmayan tanı soruları kütüphanesi.", b, "sorular.html")


def scatter(aday, top_ids):
    """Nakit ve strateji grafiği. Numaralı noktalar çakışırsa yanına kaydırılır ve gerçek konuma çizgiyle bağlanır."""
    import math
    W, Hh = 640, 430; L, R, T, B = 52, 16, 16, 44
    def X(v): return L + (W - L - R) * v / 100.0
    def Y(v): return Hh - B - (Hh - T - B) * v / 100.0
    s = ('<svg viewBox="0 0 %d %d" role="img" aria-labelledby="sc-t sc-d"><title id="sc-t">Nakit puanı ve stratejik puan</title>'
         '<desc id="sc-d">Yatay eksen kısa vadeli nakit puanı, dikey eksen stratejik puan. Numaralı noktalar yatırım sırasındaki ilk on seçenektir; değerleri grafiğin altındaki tabloda.</desc>') % (W, Hh)
    for v in (0, 20, 40, 60, 80, 100):
        s += '<line class="chart-grid" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (X(v), Y(0), X(v), Y(100))
        s += '<line class="chart-grid" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (X(0), Y(v), X(100), Y(v))
        s += '<text class="chart-text" x="%.1f" y="%.1f" text-anchor="middle">%d</text>' % (X(v), Hh - B + 16, v)
        s += '<text class="chart-text" x="%.1f" y="%.1f" text-anchor="end">%d</text>' % (L - 8, Y(v) + 4, v)
    s += '<line class="chart-axis" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/><line class="chart-axis" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (X(60), Y(0), X(60), Y(100), X(0), Y(60), X(100), Y(60))
    s += '<text class="chart-text" x="%.1f" y="%d" text-anchor="middle">Kısa vadeli nakit puanı</text>' % (X(50), Hh - 6)
    s += '<text class="chart-text" transform="translate(14 %.1f) rotate(-90)" text-anchor="middle">Stratejik puan</text>' % Y(50)
    for o in aday:
        if o["id"] in top_ids or o["stratejik"] is None: continue
        s += '<circle class="chart-pt" cx="%.1f" cy="%.1f" r="4"/>' % (X(o["nitel"]["puan"]), Y(o["stratejik"]))
    r = 9.0; placed = []; marks = ""
    for o in sorted([o for o in aday if o["id"] in top_ids and o["stratejik"] is not None], key=lambda o: o["yatirim_sirasi"]):
        x0, y0 = X(o["nitel"]["puan"]), Y(o["stratejik"]); x, y = x0, y0
        for k in range(1, 80):
            if all((x - px) ** 2 + (y - py) ** 2 >= (2 * r + 2) ** 2 for px, py in placed): break
            ang = k * 0.85; dist = 2 * r + 2 + k * 1.5
            x = min(max(x0 + dist * math.cos(ang), L + r), W - R - r); y = min(max(y0 + dist * math.sin(ang), T + r), Hh - B - r)
        placed.append((x, y))
        if (x, y) != (x0, y0):
            marks += '<line class="chart-leader" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/><circle class="chart-origin" cx="%.1f" cy="%.1f" r="2.5"/>' % (x0, y0, x, y, x0, y0)
        marks += '<circle class="chart-pt chart-pt--top" cx="%.1f" cy="%.1f" r="%.0f"/><text class="chart-num" x="%.1f" y="%.1f" text-anchor="middle">%d</text>' % (x, y, r, x, y + 3.5, o["yatirim_sirasi"])
    return s + marks + "</svg>"


def p_duyarlilik(D, yatirim, OPT):
    M = D["kriterler"]; du = D["duyarlilik"]
    b = head("Duyarlılık", "Sıralama ağırlıklara ne kadar bağlı?", "Ağırlıklar bir tercihtir, ölçüm değildir. Küçük bir ağırlık değişikliğinde birinci sıra değişiyorsa tablo bir kazanan değil, toplanması gereken veriyi göstermiştir.")
    named = du["setler"][:len(M["agirlik_setleri"])]
    rows = ""
    for s in named:
        w = s["kat"]
        rows += '<tr><th scope="row">%s</th>%s<td class="num">%s</td></tr>' % (e(s["ad"]), "".join('<td class="num">%s</td>' % num(w[k["id"]], 0 if abs(w[k["id"]] - round(w[k["id"]])) < 0.05 else 1) for k in M["kategoriler"]), num(s["spearman"], 2) if s["spearman"] is not None else "–")
    thead = "".join('<th scope="col" class="num"><span aria-hidden="true">%s</span><span class="visually-hidden">%s</span></th>' % (k["id"], e(k["ad"])) for k in M["kategoriler"])
    b += section("Beş ağırlık seti", '<div class="table-wrap" tabindex="0" role="region" aria-label="Ağırlık setleri"><table class="tbl"><thead><tr><th scope="col">Ağırlık seti</th>%s<th scope="col" class="num">Temel sırayla uyum</th></tr></thead><tbody>%s</tbody></table></div>'
                 '<p class="small muted mt-3">Kategoriler: %s. Uyum, temel sıralama ile o setin sıralaması arasındaki sıra korelasyonudur; 1 aynı sıra demektir.</p>' % (
                     thead, rows, "; ".join("%s %s" % (k["id"], e(k["ad"])) for k in M["kategoriler"])),
                 "Temel set bu çalışmanın önerisidir. Diğerleri kaynakların kendi önerdiği dağılımlar ve eşit ağırlıktır.", "setler")
    ids = [s["id"] for s in named]
    top = yatirim[:12]
    r2 = ""
    for o in top:
        d = du["secenek"][o["id"]]
        r2 += '<tr><th scope="row"><a href="proje/%s.html#%s">%s</a><br><span class="muted">%s</span></th>%s<td class="num">%d - %d</td><td class="num">%s</td></tr>' % (
            e(o["proje"]), e(o["id"]), e(o["tanim"]["ad"]), e(o["proje_baslik"]), "".join('<td class="num">%d</td>' % d["set_sira"][i] for i in ids), d["en_iyi"], d["en_kotu"], pct(d["ilk10_pay"]))
    th2 = "".join('<th scope="col" class="num">%s</th>' % e(s["ad"].split(" ")[0]) for s in named)
    nset = len(du["setler"])
    b += section("İlk 12 seçeneğin sırası nasıl oynuyor", '<div class="table-wrap" tabindex="0" role="region" aria-label="Seçeneklerin ağırlık setlerine göre sırası"><table class="tbl"><thead><tr><th scope="col">Seçenek</th>%s<th scope="col" class="num">En iyi - en kötü</th><th scope="col" class="num">İlk 10 içinde kalma</th></tr></thead><tbody>%s</tbody></table></div>'
                 '<p class="small muted mt-3">Sıralar ham puana göredir (kanıt düzeltmesi yok). En iyi ve en kötü sıra ile ilk 10 içinde kalma oranı, beş set ve her kategorinin yüzde 20 artırılıp azaltıldığı 12 ek denemenin tamamı (%d deneme) üzerinden hesaplandı.</p>' % (th2, r2, nset), None, "sira")
    stable = [o for o in top[:5] if du["secenek"][o["id"]]["ilk10_pay"] >= 0.99]
    msg = ("Yatırım sırasındaki ilk beş seçeneğin %d tanesi bütün denemelerde ilk 10'da kalıyor. " % len(stable))
    msg += "Bu seçenekler için sonuç ağırlık seçimine dayanıklı." if len(stable) >= 4 else "Sıralamanın üst kısmı ağırlık seçimine duyarlı; karar vermeden önce deneylerle kanıt toplanmalı."
    b += '<div class="wrap"><div class="callout"><p class="callout__label">Okuma</p><p>%s</p></div></div>' % e(msg)
    aday = [o for o in D["secenekler"] if o["karar"] != "kapida-kaldi"]
    top_ids = set(o["id"] for o in yatirim[:10])
    quad = {"Hem nakit hem strateji yüksek": [], "Nakit yüksek, strateji düşük": [], "Strateji yüksek, nakit düşük": [], "İkisi de düşük": []}
    for o in aday:
        if o["stratejik"] is None: continue
        hi_n = o["nitel"]["puan"] >= 60; hi_s = o["stratejik"] >= 60
        key = "Hem nakit hem strateji yüksek" if hi_n and hi_s else "Nakit yüksek, strateji düşük" if hi_n else "Strateji yüksek, nakit düşük" if hi_s else "İkisi de düşük"
        quad[key].append(o)
    ql = ""
    for k, v in quad.items():
        v = sorted(v, key=lambda o: -o["nitel"]["puan"])
        names = "".join('<li><a href="proje/%s.html#%s">%s</a> <span class="muted">· %s / %s</span></li>' % (e(o["proje"]), e(o["id"]), e(o["tanim"]["ad"]), num(o["nitel"]["puan"]), num(o["stratejik"] or 0)) for o in v[:8])
        more = '<li class="muted">ve %d seçenek daha</li>' % (len(v) - 8) if len(v) > 8 else ""
        ql += '<div><h3>%s <span class="muted small">(%d)</span></h3><ul class="bullets small mt-3">%s%s</ul></div>' % (e(k), len(v), names or '<li class="muted">yok</li>', more)
    tablo = "".join('<tr><th scope="row"><a href="proje/%s.html#%s">%d. %s</a></th><td class="num">%s</td><td class="num">%s</td></tr>' % (
        e(o["proje"]), e(o["id"]), o["yatirim_sirasi"], e(o["tanim"]["ad"]), num(o["nitel"]["puan"]), num(o["stratejik"]) if o["stratejik"] is not None else "bilinmiyor") for o in yatirim[:10])
    b += section("İki eksen: nakit ve strateji",
                 '<figure class="figure"><div class="figure__scroll" tabindex="0" role="region" aria-label="Nakit ve strateji grafiği">%s</div>'
                 '<figcaption>Numaralı noktalar yatırım sırasındaki ilk 10 seçenektir; çakışan numaralar yanına kaydırılıp gerçek konuma çizgiyle bağlandı. Çizgiler 60 puan eşiğini gösterir.</figcaption></figure>'
                 '<div class="table-wrap mt-5" tabindex="0" role="region" aria-label="İlk 10 seçeneğin değerleri"><table class="tbl"><thead><tr><th scope="col">Seçenek</th><th scope="col" class="num">Nakit puanı</th><th scope="col" class="num">Stratejik puan</th></tr></thead><tbody>%s</tbody></table></div>'
                 '<div class="split mt-6">%s</div>' % (scatter(aday, top_ids), tablo, ql),
                 "Kısa vadeli nakit puanı ile uzun vadeli stratejik puan toplanmaz. Sağ üstteki seçenekler ikisini birlikte sağlıyor; sol üsttekiler bekletme adayıdır.", "eksen")
    cdef = {c["id"]: c for c in M["kriterler"] + M["stratejik"]}
    uy = sorted(((k, v) for k, v in D["uyum"].items() if v["ortalama_fark"] is not None), key=lambda kv: -kv[1]["ortalama_fark"])
    r3 = "".join('<tr><th scope="row">%s %s</th><td class="num">%s</td><td class="num">%s</td></tr>' % (k, e(cdef[k]["ad"]), num(v["ortalama_fark"], 2), pct(v["bir_icinde"])) for k, v in uy[:10])
    allv = [v["ortalama_fark"] for _, v in uy]
    ort = (sum(allv) / len(allv)) if allv else None
    b += section("İki değerlendirici nerede ayrıştı", '<div class="table-wrap" tabindex="0" role="region" aria-label="Değerlendirici uyumu"><table class="tbl"><thead><tr><th scope="col">Kriter</th><th scope="col" class="num">Ortalama fark</th><th scope="col" class="num">Fark en çok 1</th></tr></thead><tbody>%s</tbody></table></div>' % r3,
                 "Her seçenek birbirini görmeyen iki değerlendirici tarafından puanlandı; sonra her kriter bütün seçenekler boyunca tek elden gözden geçirildi. Bütün kriterlerde ortalama fark %s puan. En çok ayrışılan on kriter aşağıda; bunlar kanıtın en zayıf olduğu yerlerdir." % (num(ort, 2) if ort is not None else "–"), "uyum")
    page("duyarlilik.html", "Duyarlılık", "Ağırlık setlerine göre sıra değişimi, iki eksenli görünüm ve değerlendirici uyumu.", b, "duyarlilik.html")


def p_portfoy(D, yatirim, kalan, OPT):
    H = D["hedef"]
    b = head("Portföy", "Birlikte yürütme ve karşılaştırma tabanı", "En yüksek puanlı üç seçeneği aynı anda seçmek doğru olmayabilir: aynı alıcıya, aynı kanala ya da aynı kişinin saatine bağlı olabilirler. Bu sayfa seçenekleri birbirine ve hiçbir şey yapmama seçeneğine karşı gösterir.")
    baz = [o for o in D["secenekler"] if o["proje"] == "baz-secenekler"]
    rows = '<tr><th scope="row">Hiçbir şey yapmamak</th><td class="num">₺0</td><td class="num">0</td><td class="num">–</td><td>Kaynak korunur; karşılaştırmanın sıfır noktası.</td></tr>'
    for o in baz:
        f = o["finans"]["baz"]
        rows += '<tr><th scope="row"><a href="proje/%s.html#%s">%s</a></th><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td>%s</td></tr>' % (e(o["proje"]), e(o["id"]), e(o["tanim"]["ad"]), tl(f["net_nakit"]), num(f["kurucu_saat"]), tl(f["saat_basi"]), e(o["karar_ad"]))
    b += section("Karşılaştırma tabanı", '<div class="table-wrap" tabindex="0" role="region" aria-label="Baz seçenekler"><table class="tbl"><thead><tr><th scope="col">Seçenek</th><th scope="col" class="num">6 ay net (baz)</th><th scope="col" class="num">Kurucu saati</th><th scope="col" class="num">Saat başı</th><th scope="col">Karar</th></tr></thead><tbody>%s</tbody></table></div>' % rows,
                 "Birinci olmak, yatırım yapılmaya değer olmak değildir. Bir proje seçeneği, aynı saatlerde yapılacak danışmanlıktan saat başına daha az nakit bırakıyorsa ancak stratejik gerekçeyle sürdürülür. Eşik: %s / saat." % tl(H["esik_saat_ucreti_tl"]), "taban")
    sb = sorted([o for o in yatirim if o["finans"]["baz"]["saat_basi"] is not None and o["proje"] != "baz-secenekler"], key=lambda o: -o["finans"]["baz"]["saat_basi"])[:12]
    r2 = "".join('<tr><th scope="row"><a href="proje/%s.html#%s">%s</a><br><span class="muted">%s</span></th><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%d</td></tr>' % (
        e(o["proje"]), e(o["id"]), e(o["tanim"]["ad"]), e(o["proje_baslik"]), tl(o["finans"]["baz"]["saat_basi"]), tl(o["finans"]["baz"]["net_nakit"]), num(o["finans"]["baz"]["kurucu_saat"]), o["yatirim_sirasi"]) for o in sb)
    gec = sum(1 for o in yatirim if o["finans"]["esik_gecer"])
    b += section("Saat başına en çok nakit bırakanlar", '<div class="table-wrap" tabindex="0" role="region" aria-label="Saat başı nakit sıralaması"><table class="tbl"><thead><tr><th scope="col">Seçenek</th><th scope="col" class="num">Saat başı (baz)</th><th scope="col" class="num">6 ay net</th><th scope="col" class="num">Saat</th><th scope="col" class="num">Yatırım sırası</th></tr></thead><tbody>%s</tbody></table></div>' % r2,
                 "Sıralamaya giren %d seçenekten %d tanesi baz senaryoda eşik saat ücretini geçiyor. Rakamlar varsayımdır; sıra, puan sırasından farklı olabilir." % (len(yatirim), gec), "saat")
    groups = {}
    for o in yatirim[:15]:
        groups.setdefault(o["etiketler"]["kanal_turu"], []).append(o)
    gl = ""
    for k, v in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        gl += '<div><h3>%s <span class="muted small">(%d)</span></h3><ul class="bullets small mt-3">%s</ul></div>' % (e(tr_capitalize(k)), len(v), "".join('<li><a href="proje/%s.html#%s">%s</a> <span class="muted">· %s</span></li>' % (e(o["proje"]), e(o["id"]), e(o["tanim"]["ad"]), e(o["etiketler"]["segment"])) for o in v))
    b += section("İlk 15 seçenek hangi kanala yaslanıyor", '<div class="split">%s</div><div class="prose mt-6"><p>Aynı kanalı ve aynı alıcıyı paylaşan iki seçenek birlikte yürütülebilir: bir görüşme ikisine de hizmet eder. Farklı alıcı ve farklı kanal isteyen iki seçenek ise kurucunun haftasını ikiye böler. Öneri: aynı anda tek satış odaklı iş; ikincisi ancak aynı alıcıya gidiyorsa.</p></div>' % gl,
                 None, "kanal")
    if kalan:
        gdef = {g["id"]: g["ad"] for g in D["kriterler"]["kapilar"]}
        r3 = "".join('<tr><th scope="row"><a href="proje/%s.html#%s">%s</a><br><span class="muted">%s</span></th><td>%s</td><td>%s</td></tr>' % (
            e(o["proje"]), e(o["id"]), e(o["tanim"]["ad"]), e(o["proje_baslik"]), e(", ".join("%s %s" % (g, gdef[g]) for g in o["kapi"]["kalanlar"])), e(o["tanim"]["kapi_duzeltme"] or "–")) for o in sorted(kalan, key=lambda o: -o["nitel"]["puan"]))
        b += section("Kapıda kalanlar (%d)" % len(kalan), '<div class="table-wrap" tabindex="0" role="region" aria-label="Kapıda kalan seçenekler"><table class="tbl"><thead><tr><th scope="col">Seçenek</th><th scope="col">Geçilemeyen kapı</th><th scope="col">Nasıl geçilir</th></tr></thead><tbody>%s</tbody></table></div>' % r3,
                     "Bu seçenekler puanlandı ama sıralamaya girmedi. Kapı geçilirse yeniden değerlendirilir.", "kapida")
    page("portfoy.html", "Portföy", "Baz seçeneklerle karşılaştırma, saat başı nakit ve birlikte yürütülebilirlik.", b, "portfoy.html")


def p_indir(D):
    os.makedirs(os.path.join(OUT, "indir"), exist_ok=True)
    slim = {"hedef": D["hedef"], "ozet": D["ozet"],
            "projeler": [{"slug": p["slug"], "baslik": p["baslik"], "tanitim": p.get("tanitim"), "secenekler": p["secenekler"]} for p in D["projeler"]],
            "secenekler": [{k: o[k] for k in ("id", "proje", "proje_baslik", "tanim", "kapilar", "kapi", "final", "nitel", "kategori", "stratejik", "finans_girdi", "finans", "deney", "etiketler", "karar", "karar_ad") if k in o} for o in D["secenekler"]]}
    for o_src, o_dst in zip(D["secenekler"], slim["secenekler"]):
        for k in ("yatirim_sirasi", "ogrenme_sirasi"):
            if k in o_src: o_dst[k] = o_src[k]
    json.dump(slim, open(os.path.join(OUT, "indir", "bpclaude-model.json"), "w", encoding="utf-8"), ensure_ascii=False)
    with open(os.path.join(OUT, "indir", "bpclaude-secenekler.csv"), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["yatirim_sirasi", "ogrenme_sirasi", "secenek", "proje", "tur", "karar", "kapi", "puan", "duzeltilmis_puan", "ortalama_kanit", "stratejik_puan", "alti_ay_net_kotu_tl", "alti_ay_net_baz_tl", "alti_ay_net_iyi_tl", "kurucu_saat_baz", "saat_basi_baz_tl", "ilk_tahsilat_gun_min", "ilk_tahsilat_gun_max", "birincil_kanal"])
        for o in sorted(D["secenekler"], key=lambda o: o.get("yatirim_sirasi", 9999)):
            f = o["finans"]
            w.writerow([o.get("yatirim_sirasi", ""), o.get("ogrenme_sirasi", ""), o["tanim"]["ad"], o["proje_baslik"], o["tanim"]["tur"], o["karar_ad"], o["kapi"]["durum"], round(o["nitel"]["puan"], 1), round(o["nitel"]["duzeltilmis"], 1), round(o["nitel"]["kanit_ort"], 2), (round(o["stratejik"], 1) if o["stratejik"] is not None else ""),
                        round(f["kotu"]["net_nakit"]), round(f["baz"]["net_nakit"]), round(f["iyi"]["net_nakit"]), round(f["baz"]["kurucu_saat"]), round(f["baz"]["saat_basi"]) if f["baz"]["saat_basi"] is not None else "", o["finans_girdi"]["ilk_tahsilat_gun"]["min"], o["finans_girdi"]["ilk_tahsilat_gun"]["max"], o["tanim"]["kanal_birincil"]])
    b = head("İndir", "Çalışma kitabı ve veri", "Şablon ve puanlar formüllü bir Excel dosyasında. Ağırlığı, puanı ya da bir finans girdisini değiştirdiğinizde sıralama yeniden hesaplanır.")
    xl = os.path.exists(os.path.join(OUT, "indir", "bpclaude-secim-sablonu.xlsx"))
    files = []
    if xl: files.append(("indir/bpclaude-secim-sablonu.xlsx", "Seçim şablonu (Excel)", "xlsx", "Hedef, kriterler, kapılar, seçenekler, puan ve kanıt, hesap, nakit, duyarlılık, deneyler, karar ekranı ve tanı soruları."))
    files.append(("indir/bpclaude-secenekler.csv", "Seçenek özeti (CSV)", "csv", "Her seçenek için sıra, karar, puan, kanıt ve altı aylık nakit; noktalı virgülle ayrılmış."))
    files.append(("indir/bpclaude-model.json", "Tam veri (JSON)", "json", "Proje tanıtımları, seçenek tanımları, kapılar, kriter puanları, gerekçeler ve hesap sonuçları."))
    b += '<div class="wrap"><ul class="linklist">%s</ul></div>' % "".join('<li><a href="%s" download><span class="linklist__title">%s</span><span class="linklist__meta">%s</span><span class="linklist__desc">%s</span></a></li>' % (e(h), e(t), e(m), e(dsc)) for h, t, m, dsc in files)
    use = ["Hedef sayfasında tutarı, kuru, haftalık saati ve eşik saat ücretini kendi rakamlarınızla değiştirin.",
           "Kriterler sayfasında kategori ağırlıklarını projelere bakmadan belirleyin; toplam 100 olmalı.",
           "Puanlar sayfasında bildiğiniz gerçekle çelişen puanı ve kanıt kodunu düzeltin. En çok değişecek kriter büyük olasılıkla ilk alıcılara doğrudan erişimdir; onu yalnız siz bilirsiniz.",
           "Deney sonuçlandığında ilgili puanı ve kanıt kodunu güncelleyin; ağırlıklara dokunmayın.",
           "Karar sayfası sıralamayı ve karar sınıfını yeniden hesaplar."]
    b += section("Nasıl kullanılır", '<ol class="prose">%s</ol>' % "".join("<li>%s</li>" % e(x) for x in use), None, "kullanim")
    page("indir.html", "İndir", "Formüllü Excel şablonu ve veri dosyaları.", b, "indir.html")


def p_hakkinda(D):
    rest = json.load(open(os.path.join(ROOT, "model", "kapsam_disi.json"), encoding="utf-8"))
    oz = D["ozet"]
    b = head("Hakkında", "Yöntem, kaynaklar ve sınırlar", "Bu belge nasıl üretildi, neye dayanıyor, neyi söylemiyor ve yayımlanırken neler dışarıda bırakıldı.")
    src = ('<div class="prose"><p>Kaynak iki ayrı çalışmadır. Birincisi 46 projeyi iş planı ve derinlik dosyasıyla ele alan Claude çalışması; ikincisi aynı proje klasörünü 141 birim (proje, sürüm, modül, rehber) olarak ele alan GPT çalışması. '
           'İki çalışma da değiştirilmedi; yalnız okundu. Proje klasörlerine yeniden gidilmedi, kod çalıştırılmadı.</p>'
           '<p>Şablon üç metinden kuruldu: aynı soruya verilmiş bir Claude araştırması, bir ChatGPT araştırması ve bir sohbet yanıtı. Soru şuydu: reklam yapmadan, bir ile altı ay arasında birkaç bin dolar getirecek proje hangi ölçütlerle seçilir?</p></div>')
    b += section("Kaynaklar", src, None, "kaynaklar")
    import glob
    hk = {"toplam": 0, "kabul": 0, "kismen": 0, "ret": 0}
    for hp in glob.glob(os.path.join(ROOT, "data", "hakem", "*.json")):
        for x in json.load(open(hp, encoding="utf-8")).get("kararlar", []):
            hk["toplam"] += 1; hk[x["karar"]] += 1
    met = ["Her proje için bir analist, iki çalışmanın belgelerini okuyup en çok üç ticari seçenek tanımladı; kapıları, finans girdilerini ve deney kartını yazdı, seçenekleri puanladı.",
           "Birbirinden bağımsız ikinci bir değerlendirici, analistin puanlarını görmeden aynı seçenekleri puanladı ve karta itirazlarını yazdı.",
           "İtirazlar proje başına ayrı bir hakem tarafından karara bağlandı: %d itirazın %d tanesi kabul edildi, %d tanesi kısmen kabul edildi, %d tanesi reddedildi. Kabul edilenler karta işlendi." % (hk["toplam"], hk["kabul"], hk["kismen"], hk["ret"]),
           "Hizmet seçeneklerinde işin kendisini yapmak için harcanan saat ayrı bir turda çıkarıldı; kurucu saati ve saat başı nakit bu teslim saatleriyle hesaplandı.",
           "Her kriter, bütün seçenekler boyunca tek elden gözden geçirildi: iki puan ve gerekçeleri çapalarla karşılaştırılıp son puan ve kanıt kodu verildi. Böylece bir projeye duyulan genel sempati kriterlere yayılmadı.",
           "Toplamlar, nakit hesabı, karar sınıfı, sıralamalar ve duyarlılık analizi kodla hesaplandı; elle düzeltme yapılmadı.",
           "Analist, değerlendirici ve gözden geçiren yapay zekâ ajanlarıdır. Kurucunun kendi puanı bu sürümde yoktur; çalışma kitabı bunun için vardır."]
    b += section("Puanlar nasıl verildi", '<ol class="prose">%s</ol>' % "".join("<li>%s</li>" % e(x) for x in met), None, "yontem")
    lim = ["Hiçbir seçenekte ödeyen müşteri kanıtı yok. Ödeme isteği kriterinde en yüksek kanıt düzeyi kaynak ve beyan düzeyidir.",
           "Kurucunun gerçek ilişki ağı belgelerde yazmıyor; ilk alıcılara doğrudan erişim kriteri bu yüzden en zayıf kanıtlı kriterdir ve ağırlığı en yüksek olanıdır. Kurucu bu puanı düzelttiğinde sıra değişebilir.",
           "Finans girdileri kaynak belgelerdeki fiyat ve senaryolardan türetildi; ölçülmüş dönüşüm oranı, müşteri kaybı ya da satış süresi yok.",
           "Vergi, ödeme altyapısı ve hukuk notları teknik okumadır; mali müşavir ve hukukçu teyidi gerekir.",
           "Puan bir tahmin modeli değildir; geçmiş sonuçlarla ayarlanmadı."]
    b += section("Sınırlar", '<ul class="bullets prose">%s</ul>' % "".join("<li>%s</li>" % e(x) for x in lim), None, "sinirlar")
    giz = ["Kişi adları yazılmadı.", "Müşteri, müşteri adayı, işveren ve iş ortağı adları yazılmadı; tanımla anıldı. Onlara ait denetim sonucu, teklif tutarı ve sözleşme bilgisi alınmadı.",
           "Kod ya da markası üçüncü tarafa ait işler yalnız markasız hizmet biçimiyle değerlendirildi; haklar kapısı bunu ayrıca gösterir.",
           "Hukuki ya da etik nedenle iş fikri sayılmayan %d klasör belgeye alınmadı." % rest["hukuki_etik_disarida"],
           "Yerel dosya yolu, sunucu adı, e-posta, güvenlik açığı ayrıntısı ve kişisel bilgi yok. Yayından önce bütün sayfalar yasaklı ifade listesiyle tarandı.",
           "Kartlar, hakem kararları ve kriter gerekçeleri yayından önce bağımsız okumayla gözden geçirildi; adı verilmeyen tarafları tanınır kılan ayrıntılar ve hukuki değerlendirme gerektiren notlar genelleştirildi.",
           "İki değerlendiricinin ham gerekçeleri yayımlanmadı. Sitede ve depoda puanları, kanıt kodları ve her kriterin kalibre edilmiş son gerekçesi durur.",
           "Site arama motorlarına kapalıdır (noindex); adresi bilen herkes açabilir."]
    b += section("Yayın kuralları", '<ul class="bullets prose">%s</ul>' % "".join("<li>%s</li>" % e(x) for x in giz), "Belge herkese açık bir adreste duruyor. Bu yüzden iki kaynak çalışmadaki bazı bilgiler bilerek dışarıda bırakıldı.", "yayin")
    rows = "".join('<tr><th scope="row">%s</th><td class="num">%d</td><td>%s</td></tr>' % (e(r["ad"]), r["adet"], e(r["neden"])) for r in rest["gruplar"])
    b += section("Değerlendirme dışı kalan birimler", '<div class="table-wrap" tabindex="0" role="region" aria-label="Değerlendirme dışı birimler"><table class="tbl"><thead><tr><th scope="col">Grup</th><th scope="col" class="num">Adet</th><th scope="col">Neden</th></tr></thead><tbody>%s</tbody></table></div>' % rows,
                 "GPT çalışmasındaki 141 birimin %d tanesi %d projeye eşlendi. Kalan %d birim ticari seçenek üretmedi." % (rest["eslenen"], oz["proje"], rest["kalan"]), "disarida")
    lis = ('<div class="prose"><p>Depo herkese açıktır; ancak açık görünürlük bir lisans değildir. Lisans kurucu tarafından seçilecek; seçilene kadar içerik için yeniden kullanım izni verilmiş sayılmaz.</p>'
           '<p>Belge yaşayan bir belgedir: bir deney sonuçlandığında ilgili puan ve kanıt kodu güncellenir, ağırlıklar yalnız hedef değiştiğinde değişir.</p></div>')
    b += section("Lisans ve güncelleme", lis, None, "lisans")
    page("hakkinda.html", "Hakkında", "Yöntem, kaynaklar, sınırlar ve yayın kuralları.", b, "hakkinda.html")


def p_404():
    b = head("Bulunamadı", "Bu sayfa yok", "Aradığınız sayfa taşınmış ya da hiç var olmamış olabilir.")
    b += '<div class="wrap"><p class="btn-row"><a class="btn" href="%sindex.html">Özete dön</a><a class="btn btn--quiet" href="%ssiralama.html">Sıralamayı aç</a></p></div>' % (BASE_PATH, BASE_PATH)
    page("404.html", "Bulunamadı", "Sayfa bulunamadı.", b, None, 0, True)


def build(D, yatirim, ogrenme, kalan, OPT):
    p_sablon(D); p_sorular(D); p_duyarlilik(D, yatirim, OPT); p_portfoy(D, yatirim, kalan, OPT); p_indir(D); p_hakkinda(D); p_404()
