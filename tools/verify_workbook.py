#!/usr/bin/env python3
"""Çalışma kitabındaki formülleri `formulas` ile hesaplatır ve sonuçları data/model.json ile karşılaştırır.
Hata hücresi ya da fark varsa çıkış kodu 1."""
import json, os, sys, tempfile, time, warnings
warnings.filterwarnings("ignore")
import formulas, openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, "docs", "indir", "bpclaude-secim-sablonu.xlsx")
D = json.load(open(os.path.join(ROOT, "data", "model.json"), encoding="utf-8"))
WM = json.load(open(os.path.join(ROOT, "data", "workbook_map.json")))
t0 = time.time()
xl = formulas.ExcelModel().loads(path).finish()
xl.calculate()
tmp = tempfile.mkdtemp()
xl.write(dirpath=tmp)
fn = [f for f in os.listdir(tmp) if f.lower().endswith(".xlsx")][0]
wb = openpyxl.load_workbook(os.path.join(tmp, fn))
S = {ws.title.upper(): ws for ws in wb.worksheets}
errs = 0; cells = 0
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if c.value is None: continue
            cells += 1
            if isinstance(c.value, str) and c.value.startswith("#"):
                errs += 1
                if errs <= 12: print("HATA HÜCRESİ", ws.title, c.coordinate, c.value)
print("hesaplanan dolu hücre: %d; hata hücresi: %d; süre %.0f sn" % (cells, errs, time.time() - t0))
hs = S["HESAP"]; fs = S["FINANS"]
FX = WM["FX"]
bad = 0; worst = 0.0
def num(v):
    return float(v) if isinstance(v, (int, float)) else None
for i, o in enumerate(D["secenekler"]):
    r = WM["R0"] + i
    assert hs["A%d" % r].value == o["id"], (hs["A%d" % r].value, o["id"])
    checks = [
        ("puan", num(hs["E%d" % r].value), o["nitel"]["puan"]),
        ("düzeltilmiş", num(hs["G%d" % r].value), o["nitel"]["duzeltilmis"]),
        ("kanıt ort", num(hs["H%d" % r].value), o["nitel"]["kanit_ort"]),
        ("stratejik", num(hs["I%d" % r].value), o["stratejik"] or 0),
        ("net baz", num(fs["%s%d" % (FX["net_baz"], r)].value), o["finans"]["baz"]["net_nakit"]),
        ("net kötü", num(fs["%s%d" % (FX["net_kotu"], r)].value), o["finans"]["kotu"]["net_nakit"]),
        ("net iyi", num(fs["%s%d" % (FX["net_iyi"], r)].value), o["finans"]["iyi"]["net_nakit"]),
        ("saat baz", num(fs["%s%d" % (FX["saat_baz"], r)].value), o["finans"]["baz"]["kurucu_saat"]),
        ("saat kötü", num(fs["%s%d" % (FX["saat_kotu"], r)].value), o["finans"]["kotu"]["kurucu_saat"]),
        ("saat iyi", num(fs["%s%d" % (FX["saat_iyi"], r)].value), o["finans"]["iyi"]["kurucu_saat"]),
        ("saat başı", num(fs["%s%d" % (FX["saat_basi"], r)].value), o["finans"]["baz"]["saat_basi"] or 0),
    ]
    for name, a, b in checks:
        d = abs((a if a is not None else 1e9) - b)
        worst = max(worst, d if d < 1e8 else 0)
        if d > 1e-6:
            bad += 1
            if bad <= 12: print("FARK", o["id"], name, a, b)
    kap = fs["%s%d" % (FX["kapasite"], r)].value
    if (kap == "hayır") != bool(o["finans"]["kapasite_asimi"]):
        bad += 1
        if bad <= 12: print("FARK kapasite", o["id"], kap, o["finans"]["kapasite_asimi"])
    if hs["N%d" % r].value != o["karar_ad"]:
        bad += 1
        if bad <= 12: print("FARK karar", o["id"], hs["N%d" % r].value, o["karar_ad"])
    for col, key in (("Q", "yatirim_sirasi"), ("T", "ogrenme_sirasi")):
        v = hs["%s%d" % (col, r)].value
        exp = o.get(key)
        got = int(round(v)) if isinstance(v, (int, float)) else None
        if got != exp:
            bad += 1
            if bad <= 12: print("FARK sıra", o["id"], key, v, exp)
# karar ekranı ilk satır
ks = S["KARAR"]
first = sorted([o for o in D["secenekler"] if "yatirim_sirasi" in o], key=lambda o: o["yatirim_sirasi"])[0]
if ks["C5"].value != first["tanim"]["ad"]:
    bad += 1; print("FARK karar ekranı ilk satır:", ks["C5"].value, "!=", first["tanim"]["ad"])
print("karşılaştırılan seçenek: %d; fark: %d; en büyük sayısal fark: %.9f" % (len(D["secenekler"]), bad, worst))
sys.exit(1 if (errs or bad) else 0)
