#!/usr/bin/env python3
"""Yayın öncesi metin düzeltmeleri: önerilen değişiklikleri denetler ve uygular.
  python3 tools/temizlik.py check <öneri.json>   önerinin birebir uygulanabildiğini denetler; TAMAM ya da hata listesi
  python3 tools/temizlik.py apply <klasör>        klasördeki bütün önerileri uygular; uygulanamayanları bildirir
Öneri biçimi: {"slug": "...", "degisiklikler": [{"dosya": "final|kart|hakem|teslim", "secenek": "<kimlik>", "kriter": "<KRITER>", "eski": "...", "yeni": "...", "tur": "..."}]}
"eski", hedef metnin içinden birebir kopyalanmış parçadır. Puan, kanıt kodu ve sayısal alanlar bu araçla değiştirilmez."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import forbidden
import validate as V

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = {"kart": "cards", "hakem": "hakem", "teslim": "teslim"}
CACHE = {}


def get(path):
    if path not in CACHE:
        CACHE[path] = json.load(open(path, encoding="utf-8"))
    return CACHE[path]


def replace_in(obj, eski, yeni):
    n = 0
    def walk(x):
        nonlocal n
        if isinstance(x, dict): return {k: walk(v) for k, v in x.items()}
        if isinstance(x, list): return [walk(v) for v in x]
        if isinstance(x, str) and eski in x:
            n += x.count(eski)
            return x.replace(eski, yeni)
        return x
    return walk(obj), n


def check_obj(kind, d, slug):
    V.errs.clear()
    {"kart": V.card, "hakem": V.hakem, "teslim": V.teslim}[kind](d, slug)
    return list(V.errs)


def run(prop):
    slug = prop.get("slug"); errs = []; done = 0
    for i, ch in enumerate(prop.get("degisiklikler", [])):
        w = "degisiklikler[%d]" % i
        kind, eski, yeni = ch.get("dosya"), ch.get("eski"), ch.get("yeni")
        if not isinstance(eski, str) or not eski.strip() or not isinstance(yeni, str):
            errs.append(w + ": eski ve yeni metin olmalı"); continue
        if eski == yeni:
            errs.append(w + ": eski ile yeni aynı"); continue
        bad = forbidden.scan(yeni)
        if bad:
            errs.append(w + ": yeni metinde yasak ifade: " + ", ".join(b[1] for b in bad)); continue
        if kind == "final":
            oid, kr = ch.get("secenek") or "", ch.get("kriter") or ""
            path = os.path.join(ROOT, "data", "final", "%s.json" % kr)
            if not os.path.exists(path):
                errs.append(w + ": kriter dosyası yok: %s" % kr); continue
            if not oid.startswith(str(slug) + "-"):
                errs.append(w + ": seçenek bu projeye ait değil: %s" % oid); continue
            x = get(path)["puanlar"].get(oid)
            if x is None:
                errs.append(w + ": seçenek bu kriterde yok: %s" % oid); continue
            g = x.get("g", "")
            if eski not in g:
                errs.append(w + ": eski metin %s %s gerekçesinde birebir bulunamadı" % (oid, kr)); continue
            ng = g.replace(eski, yeni)
            if not 10 <= len(ng) <= 200:
                errs.append(w + ": yeni gerekçe %d karakter; 10-200 olmalı" % len(ng)); continue
            x["g"] = ng; done += 1
        elif kind in DIRS:
            path = os.path.join(ROOT, "data", DIRS[kind], "%s.json" % slug)
            if not os.path.exists(path):
                errs.append(w + ": dosya yok: %s" % path); continue
            nd, n = replace_in(get(path), eski, yeni)
            if n == 0:
                errs.append(w + ": eski metin %s dosyasında birebir bulunamadı" % kind); continue
            ve = check_obj(kind, nd, slug)
            if ve:
                errs.append(w + ": değişiklik sonrası doğrulama: " + "; ".join(ve[:3])); continue
            CACHE[path] = nd; done += 1
        else:
            errs.append(w + ": dosya final, kart, hakem ya da teslim olmalı")
    return done, errs


def main():
    mode, target = sys.argv[1], sys.argv[2]
    if mode == "check":
        done, errs = run(json.load(open(target, encoding="utf-8")))
        if errs:
            print("HATA (%d):" % len(errs))
            for e in errs[:40]: print(" -", e)
            sys.exit(1)
        print("TAMAM: %d değişiklik uygulanabilir" % done)
        return
    total = 0; failed = []
    for p in sorted(glob.glob(os.path.join(target, "*.json"))):
        done, errs = run(json.load(open(p, encoding="utf-8")))
        total += done; failed += ["%s: %s" % (os.path.basename(p), e) for e in errs]
    for path, d in CACHE.items():
        json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("uygulanan: %d | uygulanamayan: %d" % (total, len(failed)))
    for e in failed: print(" -", e)


if __name__ == "__main__":
    main()
