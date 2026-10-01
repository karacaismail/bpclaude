#!/usr/bin/env python3
"""Seçim şablonunu formüllü bir Excel çalışma kitabı olarak üretir: docs/indir/bpclaude-secim-sablonu.xlsx
Girdi hücreleri mavi, formüller siyah. Ağırlık, puan, kanıt ya da finans girdisi değişince sıralama yeniden hesaplanır."""
import json, os
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "model.json"), encoding="utf-8"))
M = D["kriterler"]; H = D["hedef"]; ES = M["karar_esikleri"]
Q = json.load(open(os.path.join(ROOT, "model", "sorular.json"), encoding="utf-8"))
OPTS = D["secenekler"]
N = len(OPTS)
R0 = 5                      # ilk seçenek satırı (bütün sayfalarda aynı)
RN = R0 + N - 1
CR = M["kriterler"]; ST = M["stratejik"]
C0 = 3                      # ilk kriter sütunu (C)
CN = C0 + len(CR) - 1       # son kriter sütunu
S0 = CN + 2                 # stratejik kriterlerin ilk sütunu
SN = S0 + len(ST) - 1
COL = {c["id"]: C0 + i for i, c in enumerate(CR)}
for i, c in enumerate(ST): COL[c["id"]] = S0 + i
KR0 = 14                    # Kriterler sayfasında ilk kriter satırı
KROW = {c["id"]: KR0 + i for i, c in enumerate(CR)}
KRN = KR0 + len(CR) - 1

FONT = "Arial"
F_IN = Font(name=FONT, size=10, color="0000FF")
F_FX = Font(name=FONT, size=10, color="000000")
F_H = Font(name=FONT, size=10, bold=True, color="FFFFFF")
F_B = Font(name=FONT, size=10, bold=True)
F_T = Font(name=FONT, size=14, bold=True)
F_N = Font(name=FONT, size=9, italic=True, color="555555")
FILL_H = PatternFill("solid", fgColor="15171C")
FILL_K = PatternFill("solid", fgColor="FFF2CC")
THIN = Side(style="thin", color="D9D9D2")
WRAP = Alignment(wrap_text=True, vertical="top")
NUM0 = "#,##0;-#,##0;-"
NUM1 = "0.0"
PCT = "0%"

wb = Workbook()


def sheet(name, title, note=None, widths=None):
    ws = wb.create_sheet(name)
    ws["A1"] = title; ws["A1"].font = F_T
    if note:
        ws["A2"] = note; ws["A2"].font = F_N
    for i, w in enumerate(widths or [], 1):
        ws.column_dimensions[L(i)].width = w
    return ws


def header(ws, row, labels, col0=1):
    for i, lab in enumerate(labels):
        c = ws.cell(row, col0 + i, lab); c.font = F_H; c.fill = FILL_H; c.alignment = Alignment(wrap_text=True, vertical="center")


def put(ws, row, col, value, kind="in", fmt=None, wrap=False):
    c = ws.cell(row, col, value)
    c.font = F_IN if kind == "in" else F_B if kind == "b" else F_FX
    if fmt: c.number_format = fmt
    if wrap: c.alignment = WRAP
    return c


# ---------------------------------------------------------------- Okuma
ws = wb.active; ws.title = "Okuma"
ws["A1"] = "Proje seçim şablonu"; ws["A1"].font = F_T
lines = [
    "Bu çalışma kitabı, ücretli reklam olmadan altı ayda nakit hedefi için ticari seçenekleri karşılaştırır.",
    "Değerlendirme birimi proje değil ticari seçenektir: proje × müşteri × iş × tetikleyici × teklif ve fiyat × kanal × ilk satılabilir kapsam.",
    "",
    "Renkler: mavi yazı girdi hücresidir, değiştirilebilir. Siyah yazı formüldür, dokunulmaz. Sarı dolgulu hücreler ana kararları belirleyen varsayımlardır.",
    "",
    "Sayfalar:",
    "Hedef: hedef tutar, kur, haftalık saat, eşik saat ücreti, karar eşikleri ve kanıt ölçeği.",
    "Kriterler: altı kategori ve 26 kriter; kategori ağırlıkları toplamı 100 olmalı. Kategoriye ek puan verilmez; ağırlık kriterlere dağıtılır.",
    "Secenekler: her seçeneğin müşterisi, işi, teklifi, fiyatı ve kanalı.",
    "Kapilar: sekiz telafi edilemez koşul. Biri 'kaldi' ise seçenek sıralamaya girmez; bilinmeyen koşul 'test' yazılır.",
    "Puanlar: her kriter için 0-5 puan. C1, C2 ve D1 Finans sayfasından formülle hesaplanır. Bilinmeyen puan boş bırakılır; sıfır yazılmaz.",
    "Kanit: her puanın kanıt kodu (0-4). Guven: kanıt kodunun güven katsayısı (formül).",
    "Finans: altı aylık tahsilat, maliyet ve kurucu saati; kötü, baz ve iyi senaryo. Puanla toplanmaz.",
    "Hesap: uygunluk puanı, kanıtla düzeltilmiş puan, stratejik puan, karar sınıfı, yatırım sırası ve öğrenme sırası.",
    "Karar: yatırım sırasına göre dizilmiş karar ekranı.",
    "Duyarlilik: beş ağırlık setinde puan ve sıra; sıra çok oynuyorsa karar ağırlığa bağlıdır, veri toplanmalıdır.",
    "Deneyler: her seçeneğin sıradaki testi; sonuç geldiğinde ilgili puan ve kanıt kodu güncellenir.",
    "Tani_Sorulari: puanlanmayan soru kütüphanesi.",
    "",
    "Kullanım sırası: (1) Hedef sayfasını kendi rakamlarınızla doldurun. (2) Ağırlıkları seçeneklere bakmadan belirleyin. (3) Bildiğiniz gerçekle çelişen puanı ve kanıt kodunu düzeltin; özellikle B1 (ilk alıcılara doğrudan erişim). (4) Karar sayfasına bakın. (5) Kısa listeden bir işi seçin, deneyini yapın, sonucu işleyin.",
    "",
    "Puan bir başarı olasılığı değildir. Rakamların çoğu kaynak belgelerdeki varsayımlardır; hiçbir seçenekte ödeyen müşteri kanıtı yoktur.",
]
for i, t in enumerate(lines, 3):
    ws.cell(i, 1, t).font = Font(name=FONT, size=10); ws.cell(i, 1).alignment = WRAP
ws.column_dimensions["A"].width = 120

# ---------------------------------------------------------------- Hedef
ws = sheet("Hedef", "Hedef ve kısıtlar", H["not"], [3, 38, 16, 60])
rows = [
    ("Hedef (USD)", H["hedef_usd"], NUM0, "Altı ayda tahsil edilmiş net nakit hedefi"),
    ("Kur (₺ / USD)", H["kur_tl_usd"], NUM0, "Varsayım"),
    ("Hedef (₺)", "=C3*C4", NUM0, "Formül"),
    ("Süre (ay)", H["ufuk_ay"], NUM0, "Finans girdileri altı aya göre yazıldı; değiştirirseniz girdileri de güncelleyin"),
    ("Haftalık kurucu saati", H["haftalik_kurucu_saati"], NUM0, "C2 kriterinin hesabında kullanılır"),
    ("Eşik saat ücreti (₺)", H["esik_saat_ucreti_tl"], NUM0, "Aynı saatte danışmanlık yapmanın getirisi"),
    ("Riske edilen nakit tavanı (₺)", H["azami_riske_edilen_nakit_tl"], NUM0, "G7 kapısı için"),
    ("Uygunluk alt puanı", ES["uygunluk_alt_puan"], NUM0, "Karar kuralı"),
    ("Nakit alt oranı", ES["nakit_alt_orani"], "0.00", "Baz senaryo net nakdi hedefin bu oranına ulaşmalı"),
    ("Stratejik bekletme puanı", ES["stratejik_beklet_puan"], NUM0, "Karar kuralı"),
    ("Yatırım için ödeme kanıtı kodu", ES["yatirim_kanit_kodu"], NUM0, "A6 kanıt kodu en az bu olmalı"),
    ("Altı aylık kurucu kapasitesi (saat)", "=C7*C6*52/12", NUM0, "Formül: haftalık saat × ay × 52/12. Baz senaryoda bunu aşan seçenek nakit koşulunu sağlamış sayılmaz"),
]
for i, (lab, val, fmt, note) in enumerate(rows, 3):
    ws.cell(i, 2, lab).font = F_FX
    c = put(ws, i, 3, val, "fx" if isinstance(val, str) else "in", fmt)
    if not isinstance(val, str): c.fill = FILL_K
    ws.cell(i, 4, note).font = F_N
header(ws, 16, ["", "Kanıt kodu", "Güven katsayısı", "Anlam"])
for i, x in enumerate(M["kanit_olcegi"]):
    ws.cell(17 + i, 2, "E%d" % x["kod"]).font = F_FX
    put(ws, 17 + i, 3, x["guven"], "in", "0.0")
    ws.cell(17 + i, 4, x["tanim"]).font = F_FX
HEDEF_TL = "Hedef!$C$5"; KUR = "Hedef!$C$4"; SAAT_H = "Hedef!$C$7"; ESIK = "Hedef!$C$8"
UYG = "Hedef!$C$10"; NAKO = "Hedef!$C$11"; SBEK = "Hedef!$C$12"; YKK = "Hedef!$C$13"; KAP = "Hedef!$C$14"
GUV = "Hedef!$C$17:$C$21"

# ---------------------------------------------------------------- Kriterler
ws = sheet("Kriterler", "Kategoriler ve kriterler", "Kategori ağırlıklarını seçeneklere bakmadan belirleyin. Toplam 100 olmalı.", [3, 8, 34, 14, 14, 14, 9, 52, 42, 42, 42, 30])
header(ws, 3, ["", "Kategori", "Ad", "Ağırlık"])
for i, k in enumerate(M["kategoriler"]):
    r = 4 + i
    ws.cell(r, 2, k["id"]).font = F_B; ws.cell(r, 3, k["ad"]).font = F_FX
    put(ws, r, 4, k["agirlik"], "in", NUM0).fill = FILL_K
ws.cell(10, 3, "Toplam").font = F_B; put(ws, 10, 4, "=SUM(D4:D9)", "fx", NUM0)
put(ws, 10, 5, '=IF(ROUND(D10,6)=100,"tamam","toplam 100 olmalı")', "fx")
header(ws, 13, ["", "ID", "Ad", "Kategori", "Kategori içi ağırlık", "Toplamdaki ağırlık", "Yön", "Soru", "1 puan", "3 puan", "5 puan", "Kanıt türü"])
for c in CR:
    r = KROW[c["id"]]
    ws.cell(r, 2, c["id"]).font = F_B; ws.cell(r, 3, c["ad"]).font = F_FX; ws.cell(r, 3).alignment = WRAP
    ws.cell(r, 4, c["kat"]).font = F_FX
    put(ws, r, 5, c["agirlik"], "in", NUM1)
    put(ws, r, 6, "=INDEX($D$4:$D$9,MATCH(D%d,$B$4:$B$9,0))*E%d/SUMIF($D$%d:$D$%d,D%d,$E$%d:$E$%d)" % (r, r, KR0, KRN, r, KR0, KRN), "fx", "0.00")
    ws.cell(r, 7, "ters" if c["yon"] == "ters" else "fayda").font = F_FX
    for j, key in enumerate(("soru", "c1", "c3", "c5", "kanit")):
        ws.cell(r, 8 + j, c[key]).font = F_FX; ws.cell(r, 8 + j).alignment = WRAP
ws.cell(KRN + 1, 3, "Toplam").font = F_B; put(ws, KRN + 1, 6, "=SUM(F%d:F%d)" % (KR0, KRN), "fx", "0.00")
SR0 = KRN + 5
header(ws, SR0 - 1, ["", "ID", "Stratejik kriter", "", "Ağırlık", "", "", "Soru", "1 puan", "3 puan", "5 puan"])
for i, c in enumerate(ST):
    r = SR0 + i
    ws.cell(r, 2, c["id"]).font = F_B; ws.cell(r, 3, c["ad"]).font = F_FX
    put(ws, r, 5, c["agirlik"], "in", NUM0)
    for j, key in enumerate(("soru", "c1", "c3", "c5")):
        ws.cell(r, 8 + j, c[key]).font = F_FX; ws.cell(r, 8 + j).alignment = WRAP
ws.freeze_panes = "D14"

# ---------------------------------------------------------------- Secenekler
ws = sheet("Secenekler", "Ticari seçenekler", "Her satır bir seçenektir; satır numarası bütün sayfalarda aynıdır.", [22, 34, 40, 14, 40, 44, 36, 44, 30, 40, 36, 36, 46, 26, 16, 16])
header(ws, 4, ["Kimlik", "Proje", "Seçenek", "Tür", "Müşteri", "Müşterinin işi", "Tetikleyici", "Teklif", "Fiyat", "Birincil kanal", "Yedek kanal", "İlk adım", "İlk satılabilir kapsam", "Segment", "Kanal türü", "Düzenleme"])
for i, o in enumerate(OPTS):
    r = R0 + i; t = o["tanim"]
    vals = [o["id"], o["proje_baslik"], t["ad"], t["tur"], t["musteri"], t["is"], t["tetikleyici"], t["teklif"], t["fiyat"], t["kanal_birincil"], t["kanal_yedek"], t["ilk_adim"], t["ilk_kapsam"], o["etiketler"]["segment"], o["etiketler"]["kanal_turu"], o["etiketler"]["regulasyon"]]
    for j, v in enumerate(vals, 1):
        put(ws, r, j, v, "in", wrap=True)
ws.freeze_panes = "D5"

# ---------------------------------------------------------------- Kapilar
ws = sheet("Kapilar", "Kapılar", "Değerler: gecti, test, kaldi. Biri kaldi ise sonuç kaldi; değilse biri test ise sonuç test.", [22, 40] + [10] * 8 + [10, 60])
header(ws, 4, ["Kimlik", "Seçenek"] + ["%s %s" % (g["id"], g["ad"]) for g in M["kapilar"]] + ["Sonuç", "Kapılar nasıl geçilir"])
dv = DataValidation(type="list", formula1='"gecti,test,kaldi"', allow_blank=False); ws.add_data_validation(dv)
for i, o in enumerate(OPTS):
    r = R0 + i
    put(ws, r, 1, "=Secenekler!A%d" % r, "fx"); put(ws, r, 2, "=Secenekler!C%d" % r, "fx")
    for j, g in enumerate(M["kapilar"]):
        c = put(ws, r, 3 + j, o["kapilar"][g["id"]]["durum"], "in"); dv.add(c)
    put(ws, r, 11, '=IF(COUNTIF(C%d:J%d,"kaldi")>0,"kaldi",IF(COUNTIF(C%d:J%d,"test")>0,"test","gecti"))' % (r, r, r, r), "fx")
    put(ws, r, 12, o["tanim"]["kapi_duzeltme"], "in", wrap=True)
ws.freeze_panes = "C5"

# ---------------------------------------------------------------- Finans
FC = ["satis_tipi", "net_fiyat", "degisken", "sabit", "baslangic", "efor_min", "efor_bek", "efor_max", "gun_min", "gun_max", "satis_saat", "teslim_saat", "destek_dk",
      "tah_kotu", "tah_baz", "tah_iyi", "ode_kotu", "ode_baz", "ode_iyi", "mus_kotu", "mus_baz", "mus_iyi", "don_dusuk", "don_yuksek"]
FX = {k: L(3 + i) for i, k in enumerate(FC)}          # C..Y
OUTC = ["net_kotu", "net_baz", "net_iyi", "saat_kotu", "saat_baz", "saat_iyi", "saat_basi", "katki", "gerekli", "aday_min", "aday_max", "riske", "hedef", "esik", "kapasite", "net_usd"]
for i, k in enumerate(OUTC): FX[k] = L(3 + len(FC) + i)   # Z..AN
ws = sheet("Finans", "Altı aylık nakit hesabı", "Tutarlar ₺, KDV hariç. Mavi sütunlar girdi; sağdaki siyah sütunlar formül. Kurucu saati = kalan efor + müşteri × satış saati + ödeme adedi × (teslim saati + destek dakikası ÷ 60).", [22, 40] + [13] * (len(FC) + len(OUTC)))
header(ws, 4, ["Kimlik", "Seçenek", "Satış tipi", "Net fiyat", "Ödeme başına değişken maliyet", "Aylık sabit gider", "Başlangıç harcaması", "Kalan efor en az (saat)", "Kalan efor beklenen", "Kalan efor en çok",
               "İlk tahsilat en erken (gün)", "İlk tahsilat en geç", "Satış başına kurucu saati", "Ödeme başına teslim saati", "Müşteri başına aylık destek (dk)", "Tahsilat kötü", "Tahsilat baz", "Tahsilat iyi", "Ödeme adedi kötü", "Ödeme adedi baz", "Ödeme adedi iyi",
               "Müşteri kötü", "Müşteri baz", "Müşteri iyi", "Dönüşüm düşük", "Dönüşüm yüksek",
               "Net nakit kötü", "Net nakit baz", "Net nakit iyi", "Kurucu saati kötü", "Kurucu saati baz", "Kurucu saati iyi", "Saat başı nakit (baz)", "Müşteri başına katkı", "Hedef için gereken müşteri", "Gereken aday en az", "Gereken aday en çok",
               "Riske edilen nakit", "Baz hedefe ulaşıyor mu", "Eşik saat ücretini geçiyor mu", "Kapasite içinde mi", "Net nakit baz (USD)"])
ws.row_dimensions[4].height = 44
for i, o in enumerate(OPTS):
    r = R0 + i; f = o["finans_girdi"]
    put(ws, r, 1, "=Secenekler!A%d" % r, "fx"); put(ws, r, 2, "=Secenekler!C%d" % r, "fx")
    vals = [f["satis_tipi"], f["net_fiyat_tl"], f["degisken_maliyet_tl"], f["sabit_gider_aylik_tl"], f["baslangic_nakit_tl"], f["kalan_efor_saat"]["min"], f["kalan_efor_saat"]["beklenen"], f["kalan_efor_saat"]["max"],
            f["ilk_tahsilat_gun"]["min"], f["ilk_tahsilat_gun"]["max"], f["satis_basina_kurucu_saati"], f.get("teslim_saat_odeme_basina", 0), f["musteri_basina_aylik_destek_dk"],
            f["alti_ay_tahsilat_tl"]["kotu"], f["alti_ay_tahsilat_tl"]["baz"], f["alti_ay_tahsilat_tl"]["iyi"], f["alti_ay_odeme_adedi"]["kotu"], f["alti_ay_odeme_adedi"]["baz"], f["alti_ay_odeme_adedi"]["iyi"],
            f["alti_ay_musteri"]["kotu"], f["alti_ay_musteri"]["baz"], f["alti_ay_musteri"]["iyi"], f["donusum_orani"]["dusuk"], f["donusum_orani"]["yuksek"]]
    for j, v in enumerate(vals):
        put(ws, r, 3 + j, v, "in", None if j == 0 else ("0.000" if FC[j].startswith("don_") else NUM0))
    X = lambda k: "%s%d" % (FX[k], r)
    fx = {
        "net_kotu": "=%s-%s*%s-6*%s-%s" % (X("tah_kotu"), X("ode_kotu"), X("degisken"), X("sabit"), X("baslangic")),
        "net_baz": "=%s-%s*%s-6*%s-%s" % (X("tah_baz"), X("ode_baz"), X("degisken"), X("sabit"), X("baslangic")),
        "net_iyi": "=%s-%s*%s-6*%s-%s" % (X("tah_iyi"), X("ode_iyi"), X("degisken"), X("sabit"), X("baslangic")),
        "saat_kotu": "=%s+%s*%s+%s*(%s+%s/60)" % (X("efor_max"), X("mus_kotu"), X("satis_saat"), X("ode_kotu"), X("teslim_saat"), X("destek_dk")),
        "saat_baz": "=%s+%s*%s+%s*(%s+%s/60)" % (X("efor_bek"), X("mus_baz"), X("satis_saat"), X("ode_baz"), X("teslim_saat"), X("destek_dk")),
        "saat_iyi": "=%s+%s*%s+%s*(%s+%s/60)" % (X("efor_min"), X("mus_iyi"), X("satis_saat"), X("ode_iyi"), X("teslim_saat"), X("destek_dk")),
        "saat_basi": "=IF(%s>0,%s/%s,0)" % (X("saat_baz"), X("net_baz"), X("saat_baz")),
        "katki": "=IF(%s>0,(%s-%s*%s)/%s,%s-%s)" % (X("mus_baz"), X("tah_baz"), X("ode_baz"), X("degisken"), X("mus_baz"), X("net_fiyat"), X("degisken")),
        "gerekli": "=IF(%s>0,(%s+6*%s+%s)/%s,0)" % (X("katki"), HEDEF_TL, X("sabit"), X("baslangic"), X("katki")),
        "aday_min": "=IF(%s>0,%s/%s,0)" % (X("gerekli"), X("gerekli"), X("don_yuksek")),
        "aday_max": "=IF(%s>0,%s/%s,0)" % (X("gerekli"), X("gerekli"), X("don_dusuk")),
        "riske": "=%s+%s*%s/30" % (X("baslangic"), X("sabit"), X("gun_max")),
        "hedef": '=IF(%s>=%s,"evet","hayır")' % (X("net_baz"), HEDEF_TL),
        "esik": '=IF(%s>=%s,"evet","hayır")' % (X("saat_basi"), ESIK),
        "kapasite": '=IF(%s<=%s,"evet","hayır")' % (X("saat_baz"), KAP),
        "net_usd": "=%s/%s" % (X("net_baz"), KUR),
    }
    for k in OUTC:
        put(ws, r, 3 + len(FC) + OUTC.index(k), fx[k], "fx", None if k in ("hedef", "esik", "kapasite") else NUM0)
ws.freeze_panes = "C5"

# ---------------------------------------------------------------- Puanlar, Kanit, Guven
def grid(name, title, note, kind):
    ws = sheet(name, title, note, [22, 40] + [7] * (SN - 2))
    ws.cell(4, 1, "Kimlik").font = F_H; ws.cell(4, 1).fill = FILL_H; ws.cell(4, 2, "Seçenek").font = F_H; ws.cell(4, 2).fill = FILL_H
    for c in CR + ST:
        col = COL[c["id"]]
        h = ws.cell(4, col, c["id"]); h.font = F_H; h.fill = FILL_H; h.alignment = Alignment(horizontal="center")
        if kind == "puan":
            if c in CR:
                put(ws, 3, col, "=Kriterler!F%d" % KROW[c["id"]], "fx", "0.0")
            else:
                put(ws, 3, col, "=Kriterler!E%d" % (SR0 + ST.index(c)), "fx", "0.0")
    if kind == "puan":
        ws.cell(3, 2, "Ağırlık").font = F_B
    for i, o in enumerate(OPTS):
        r = R0 + i
        put(ws, r, 1, "=Secenekler!A%d" % r, "fx"); put(ws, r, 2, "=Secenekler!C%d" % r, "fx")
        for c in CR + ST:
            col = COL[c["id"]]; x = o["final"].get(c["id"]) or {}
            if kind == "puan":
                if c["id"] == "C1":
                    m = "(Finans!%s%d+Finans!%s%d)/2" % (FX["gun_min"], r, FX["gun_max"], r)
                    put(ws, r, col, "=IF(%s<14,5,IF(%s<28,4,IF(%s<=56,3,IF(%s<=90,2,1))))" % (m, m, m, m), "fx", "0")
                elif c["id"] == "C2":
                    w = "Finans!%s%d/%s" % (FX["efor_bek"], r, SAAT_H)
                    put(ws, r, col, "=IF(%s<1,5,IF(%s<3,4,IF(%s<=5,3,IF(%s<=8,2,1))))" % (w, w, w, w), "fx", "0")
                elif c["id"] == "D1":
                    g = "Finans!%s%d" % (FX["gerekli"], r)
                    put(ws, r, col, "=IF(%s<=0,0,IF(%s<=5,5,IF(%s<10,4,IF(%s<=30,3,IF(%s<100,2,1)))))" % (g, g, g, g, g), "fx", "0")
                else:
                    put(ws, r, col, x.get("p"), "in", "0")
            elif kind == "kanit":
                put(ws, r, col, x.get("k", 0), "in", "0")
            else:
                put(ws, r, col, "=INDEX(%s,Kanit!%s%d+1)" % (GUV, L(col), r), "fx", "0.0")
    ws.freeze_panes = "C5"
    return ws


grid("Puanlar", "Puanlar (0-5)", "Mavi hücreler değiştirilebilir. C1, C2 ve D1 Finans sayfasından hesaplanır. Bilinmeyen puan boş bırakılır.", "puan")
grid("Kanit", "Kanıt kodları (0-4)", "0 varsayım, 1 kaynak ya da beyan, 2 davranış, 3 ödeme, 4 tekrarlanan ödeme.", "kanit")
grid("Guven", "Güven katsayıları", "Kanıt kodunun Hedef sayfasındaki katsayısı. Formül; değiştirmeyin.", "guven")
PW = "Puanlar!$%s$3:$%s$3" % (L(C0), L(CN))
SW = "Puanlar!$%s$3:$%s$3" % (L(S0), L(SN))

# ---------------------------------------------------------------- Deneyler
ws = sheet("Deneyler", "Deney kartları", "Sonuç geldiğinde K-M sütunlarını doldurun; ilgili puanı ve kanıt kodunu güncelleyin.", [22, 40, 46, 52, 10, 12, 12, 40, 40, 40, 30, 14, 20])
header(ws, 4, ["Kimlik", "Seçenek", "En riskli varsayım", "Yöntem", "Süre (gün)", "Maliyet (saat)", "Maliyet (₺)", "Başarı ölçütü", "Bırakma ölçütü", "Başarılıysa açılacak dilim", "Sonuç", "Tarih", "Karar"])
for i, o in enumerate(OPTS):
    r = R0 + i; d = o["deney"]
    put(ws, r, 1, "=Secenekler!A%d" % r, "fx"); put(ws, r, 2, "=Secenekler!C%d" % r, "fx")
    for j, v in enumerate([d["varsayim"], d["yontem"], d["sure_gun"], d["maliyet_saat"], d["maliyet_tl"], d["basari_olcutu"], d["birakma_olcutu"], d["sonraki_dilim"]]):
        put(ws, r, 3 + j, v, "in", NUM0 if isinstance(v, (int, float)) else None, wrap=True)
ws.freeze_panes = "C5"

# ---------------------------------------------------------------- Hesap
ws = sheet("Hesap", "Hesap", "Bütün sütunlar formüldür.", [22, 40, 34, 9, 9, 9, 11, 9, 10, 14, 8, 8, 8, 14, 8, 14, 10, 12, 14, 10])
header(ws, 4, ["Kimlik", "Seçenek", "Proje", "Kapı", "Uygunluk puanı", "Puanlanan ağırlık", "Kanıtla düzeltilmiş puan", "Ortalama kanıt", "Stratejik puan", "6 ay net nakit (baz)", "A6 kanıt", "Uygunluk yeterli", "Nakit yeterli", "Karar", "Sınıf", "Sıra anahtarı", "Yatırım sırası", "Öğrenme endeksi", "Öğrenme anahtarı", "Öğrenme sırası"])
ws.row_dimensions[4].height = 44
PRNG = lambda r: "Puanlar!%s%d:%s%d" % (L(C0), r, L(CN), r)
for i, o in enumerate(OPTS):
    r = R0 + i
    fx = [
        "=Secenekler!A%d" % r, "=Secenekler!C%d" % r, "=Secenekler!B%d" % r, "=Kapilar!K%d" % r,
        "=SUMPRODUCT(%s,%s)/5" % (PW, PRNG(r)),
        '=SUMIF(%s,">=0",%s)' % (PRNG(r), PW),
        "=SUMPRODUCT(%s,%s,Guven!%s%d:%s%d)/5" % (PW, PRNG(r), L(C0), r, L(CN), r),
        "=SUMPRODUCT(%s,Kanit!%s%d:%s%d)/SUM(%s)" % (PW, L(C0), r, L(CN), r, PW),
        "=SUMPRODUCT(%s,Puanlar!%s%d:%s%d)/5" % (SW, L(S0), r, L(SN), r),
        "=Finans!%s%d" % (FX["net_baz"], r),
        "=Kanit!%s%d" % (L(COL["A6"]), r),
        "=IF(E%d>=%s,1,0)" % (r, UYG),
        "=IF(AND(J%d>=%s*%s,Finans!%s%d<=%s),1,0)" % (r, HEDEF_TL, NAKO, FX["saat_baz"], r, KAP),
        '=IF(D%d="kaldi","Kapıda kaldı",IF(AND(D%d="gecti",L%d=1,K%d>=%s,J%d>=%s),"Yatırım yap",IF(AND(L%d=1,M%d=1),"Önce test et",IF(OR(L%d=1,M%d=1),"Değiştir",IF(I%d>=%s,"Beklet","Bırak")))))' % (r, r, r, r, YKK, r, HEDEF_TL, r, r, r, r, r, SBEK),
        '=IF(N%d="Yatırım yap",0,IF(N%d="Önce test et",1,IF(N%d="Değiştir",2,IF(N%d="Beklet",3,IF(N%d="Bırak",4,9)))))' % (r, r, r, r, r),
        '=IF(D%d="kaldi","",O%d*1000-G%d+%d/1000000000)' % (r, r, r, r),
        '=IF(D%d="kaldi","",1+COUNTIF($P$%d:$P$%d,"<"&P%d))' % (r, R0, RN, r),
        '=IF(D%d="kaldi","",E%d*(1-IF(E%d>0,G%d/E%d,0))/MAX(1,Deneyler!F%d))' % (r, r, r, r, r, r),
        '=IF(D%d="kaldi","",-R%d+%d/1000000000)' % (r, r, r),
        '=IF(D%d="kaldi","",1+COUNTIF($S$%d:$S$%d,"<"&S%d))' % (r, R0, RN, r),
    ]
    fmts = [None, None, None, None, "0.0", "0.0", "0.0", "0.00", "0.0", NUM0, "0", "0", "0", None, "0", "0.000000000", "0", "0.000", "0.000000000", "0"]
    for j, v in enumerate(fx):
        put(ws, r, 1 + j, v, "fx", fmts[j])
ws.freeze_panes = "C5"

# ---------------------------------------------------------------- Karar
ws = sheet("Karar", "Karar ekranı", "Yatırım sırasına göre. Kapıda kalan seçenekler listede yer almaz. Bütün hücreler formüldür.", [7, 9, 44, 34, 14, 8, 9, 11, 9, 10, 14, 12, 12, 12, 60])
header(ws, 4, ["Sıra", "Satır", "Seçenek", "Proje", "Karar", "Kapı", "Uygunluk puanı", "Düzeltilmiş puan", "Ortalama kanıt", "Stratejik puan", "6 ay net nakit (baz)", "Saat başı nakit", "İlk tahsilat en erken (gün)", "Öğrenme sırası", "Sıradaki deneyin varsayımı"])
ws.row_dimensions[4].height = 44
HQ = "Hesap!$Q$%d:$Q$%d" % (R0, RN)
def idx(sheet_col, r):
    return '=IF(B%d="","",INDEX(%s,B%d))' % (r, sheet_col, r)
for i in range(N):
    r = R0 + i
    put(ws, r, 1, i + 1, "fx", "0")
    put(ws, r, 2, '=IFERROR(MATCH(A%d,%s,0),"")' % (r, HQ), "fx", "0")
    cols = ["Hesap!$B$%d:$B$%d", "Hesap!$C$%d:$C$%d", "Hesap!$N$%d:$N$%d", "Hesap!$D$%d:$D$%d", "Hesap!$E$%d:$E$%d", "Hesap!$G$%d:$G$%d", "Hesap!$H$%d:$H$%d", "Hesap!$I$%d:$I$%d", "Hesap!$J$%d:$J$%d",
            "Finans!$" + FX["saat_basi"] + "$%d:$" + FX["saat_basi"] + "$%d", "Finans!$" + FX["gun_min"] + "$%d:$" + FX["gun_min"] + "$%d", "Hesap!$T$%d:$T$%d", "Deneyler!$C$%d:$C$%d"]
    fm = [None, None, None, None, "0.0", "0.0", "0.00", "0.0", NUM0, NUM0, "0", "0", None]
    for j, cdef in enumerate(cols):
        c = put(ws, r, 3 + j, idx(cdef % (R0, RN), r), "fx", fm[j]); 
        if j in (0, 1, 12): c.alignment = WRAP
ws.freeze_panes = "C5"

# ---------------------------------------------------------------- Duyarlilik
ws = sheet("Duyarlilik", "Ağırlık duyarlılığı", "Beş ağırlık setinde uygunluk puanı ve sıra. Kategori ağırlıklarını (mavi) değiştirerek kendi setinizi deneyebilirsiniz.", [22, 40] + [8] * (CN - 2 + 14))
header(ws, 4, ["Set", "Ad"] + [k["id"] for k in M["kategoriler"]] + ["Toplam"])
SETS = M["agirlik_setleri"]
for i, s in enumerate(SETS):
    r = 5 + i
    ws.cell(r, 1, s["id"]).font = F_B; ws.cell(r, 2, s["ad"]).font = F_FX
    for j, k in enumerate(M["kategoriler"]):
        put(ws, r, 3 + j, s["kat"][k["id"]], "in", "0.0")
    put(ws, r, 9, "=SUM(C%d:H%d)" % (r, r), "fx", "0.0")
WR0 = 13
header(ws, WR0 - 1, ["Set", "Kriter ağırlıkları"] + [c["id"] for c in CR])
for i, s in enumerate(SETS):
    r = WR0 + i
    ws.cell(r, 1, s["id"]).font = F_B
    for c in CR:
        kr = KROW[c["id"]]; catcol = L(3 + [k["id"] for k in M["kategoriler"]].index(c["kat"]))
        put(ws, r, COL[c["id"]], "=$%s$%d*Kriterler!$E$%d/SUMIF(Kriterler!$D$%d:$D$%d,Kriterler!$D$%d,Kriterler!$E$%d:$E$%d)" % (catcol, 5 + i, kr, KR0, KRN, kr, KR0, KRN), "fx", "0.00")
DR0 = 22
ns = len(SETS)
header(ws, DR0 - 1, ["Kimlik", "Seçenek"] + ["Puan: %s" % s["id"] for s in SETS] + ["Sıra: %s" % s["id"] for s in SETS] + ["En iyi sıra", "En kötü sıra"])
ws.row_dimensions[DR0 - 1].height = 30
for i, o in enumerate(OPTS):
    r = DR0 + i; hr = R0 + i
    put(ws, r, 1, "=Secenekler!A%d" % hr, "fx"); put(ws, r, 2, "=Secenekler!C%d" % hr, "fx")
    for j in range(ns):
        wr = WR0 + j
        put(ws, r, 3 + j, '=IF(Hesap!D%d="kaldi","",SUMPRODUCT($%s$%d:$%s$%d,%s)/5)' % (hr, L(C0), wr, L(CN), wr, PRNG(hr)), "fx", "0.0")
    for j in range(ns):
        pc = L(3 + j)
        put(ws, r, 3 + ns + j, '=IF(%s%d="","",1+COUNTIF($%s$%d:$%s$%d,">"&%s%d))' % (pc, r, pc, DR0, pc, DR0 + N - 1, pc, r), "fx", "0")
    a, b = L(3 + ns), L(3 + 2 * ns - 1)
    put(ws, r, 3 + 2 * ns, '=IF(%s%d="","",MIN(%s%d:%s%d))' % (a, r, a, r, b, r), "fx", "0")
    put(ws, r, 4 + 2 * ns, '=IF(%s%d="","",MAX(%s%d:%s%d))' % (a, r, a, r, b, r), "fx", "0")
ws.freeze_panes = "C%d" % DR0

# ---------------------------------------------------------------- Tani_Sorulari
ws = sheet("Tani_Sorulari", "Tanı soruları (puanlanmaz)", Q["not"], [26, 9, 96, 14, 40])
header(ws, 4, ["Grup", "Kriter", "Soru", "Yanıt (evet / hayır / bilinmiyor)", "Not"])
r = 5
for g in Q["gruplar"]:
    for cid, q in g["sorular"]:
        ws.cell(r, 1, g["ad"]).font = F_FX; ws.cell(r, 2, cid).font = F_B
        c = ws.cell(r, 3, q); c.font = F_FX; c.alignment = WRAP
        r += 1
ws.freeze_panes = "A5"

order = ["Okuma", "Karar", "Hedef", "Kriterler", "Secenekler", "Kapilar", "Puanlar", "Kanit", "Finans", "Hesap", "Duyarlilik", "Deneyler", "Tani_Sorulari", "Guven"]
wb._sheets = [wb[n] for n in order]
out = os.path.join(ROOT, "docs", "indir", "bpclaude-secim-sablonu.xlsx")
os.makedirs(os.path.dirname(out), exist_ok=True)
wb.properties.creator = "bpclaude"
wb.properties.lastModifiedBy = "bpclaude"
wb.properties.title = "bpclaude seçim şablonu"
wb.save(out)
json.dump({"R0": R0, "N": N, "ids": [o["id"] for o in OPTS], "FX": FX}, open(os.path.join(ROOT, "data", "workbook_map.json"), "w"))
print("yazıldı:", out, "| seçenek:", N)
