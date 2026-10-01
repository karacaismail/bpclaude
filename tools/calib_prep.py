#!/usr/bin/env python3
"""Kalibrasyon girdilerini hazırlar: bütün seçeneklerin özet kartı ve kriter başına A/B puanları."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, "model", "criteria.json"), encoding="utf-8"))
MAP = json.load(open(os.path.join(ROOT, "model", "projeler.json"), encoding="utf-8"))
HESAPLANAN = ("C1", "C2", "D1")  # finans girdilerinden kodla hesaplanır; kalibrasyona girmez
out = ["# Seçenek özet kartları", ""]
rows = {c["id"]: [] for c in M["kriterler"] + M["stratejik"]}
n = 0
for m in MAP:
    cp = os.path.join(ROOT, "data", "cards", m["slug"] + ".json")
    if not os.path.exists(cp): continue
    card = json.load(open(cp, encoding="utf-8"))
    sc = {}
    for r in ("A", "B"):
        p = os.path.join(ROOT, "private", "scores_full", "%s.%s.json" % (m["slug"], r))
        if not os.path.exists(p):  # depodan alınan kopyada gerekçesiz herkese açık dosya kullanılır
            p = os.path.join(ROOT, "data", "scores", "%s.%s.json" % (m["slug"], r))
        sc[r] = json.load(open(p, encoding="utf-8")).get("puanlar", {}) if os.path.exists(p) else {}
    out += ["## Proje: %s" % card["baslik"], "Özet: %s" % card["ozet"], "Bugün var: %s" % "; ".join(card["bugun"]["var"]), "Henüz yok: %s" % "; ".join(card["bugun"]["yok"]), "Ödeyen müşteri: %s" % card["bugun"]["odeyen_musteri"], ""]
    for o in card["secenekler"]:
        n += 1
        f = o["finans"]
        kap = ", ".join("%s %s" % (g, v["durum"]) for g, v in sorted(o["kapilar"].items()))
        out += ["### %s — %s (%s)" % (o["id"], o["ad"], o["tur"]),
                "- Müşteri: %s" % o["musteri"], "- İş: %s" % o["is"], "- Tetikleyici: %s" % o["tetikleyici"], "- Teklif: %s" % o["teklif"], "- Fiyat: %s" % o["fiyat"],
                "- Kanal: %s | Yedek: %s | İlk adım: %s" % (o["kanal_birincil"], o["kanal_yedek"], o["ilk_adim"]), "- İlk kapsam: %s" % o["ilk_kapsam"], "- Kapılar: %s" % kap,
                "- Finans: %s; net fiyat %s TL; kalan efor %s-%s-%s saat; ilk tahsilat %s-%s gün; satış başına %s saat; aylık destek %s dk; 6 ay tahsilat kötü/baz/iyi %s/%s/%s TL; müşteri %s/%s/%s" % (
                    f["satis_tipi"], f["net_fiyat_tl"], f["kalan_efor_saat"]["min"], f["kalan_efor_saat"]["beklenen"], f["kalan_efor_saat"]["max"], f["ilk_tahsilat_gun"]["min"], f["ilk_tahsilat_gun"]["max"],
                    f["satis_basina_kurucu_saati"], f["musteri_basina_aylik_destek_dk"], f["alti_ay_tahsilat_tl"]["kotu"], f["alti_ay_tahsilat_tl"]["baz"], f["alti_ay_tahsilat_tl"]["iyi"], f["alti_ay_musteri"]["kotu"], f["alti_ay_musteri"]["baz"], f["alti_ay_musteri"]["iyi"]),
                "- Kanıt notları: %s" % o["kanit_notlari"], ""]
        for c in rows:
            rows[c].append({"id": o["id"], "A": sc["A"].get(o["id"], {}).get(c), "B": sc["B"].get(o["id"], {}).get(c)})
os.makedirs(os.path.join(ROOT, "data", "calib"), exist_ok=True)
open(os.path.join(ROOT, "data", "calib", "kartlar.md"), "w", encoding="utf-8").write("\n".join(out))
for c, r in rows.items():
    if c in HESAPLANAN: continue
    json.dump({"kriter": c, "secenekler": r}, open(os.path.join(ROOT, "data", "calib", c + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("seçenek:", n, "| kartlar.md satır:", len(out), "| karakter:", sum(len(x) for x in out), "| kriter dosyası:", len(rows) - len(HESAPLANAN))
