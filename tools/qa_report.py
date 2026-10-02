#!/usr/bin/env python3
"""Son Playwright koşusundan (test-results/results.json) kanıt raporu üretir: qa/RAPOR.md
Rapor elle yazılmaz. Otomatik çalışmayan katmanlar qa/manual.json dosyasından okunur ve durumları olduğu gibi yazılır."""
import collections, datetime, json, os, platform, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "test-results", "results.json")
if not os.path.exists(SRC):
    print("test-results/results.json yok; önce npm test çalıştırın"); sys.exit(1)
R = json.load(open(SRC, encoding="utf-8"))

KATMAN = {"layout.spec.js": "Yerleşim", "interaction.spec.js": "Etkileşim ve durum geçişleri", "network.spec.js": "Ağ ve bütünlük", "a11y.spec.js": "Erişilebilirlik", "kabul.spec.js": "Tasarım kabul ölçütleri", "visual.spec.js": "Görsel karşılaştırma"}
PROFIL = {
    "chromium": ("Chromium", "1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır)", "fare ve klavye"),
    "firefox": ("Firefox", "1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır)", "fare ve klavye"),
    "webkit": ("WebKit", "1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır)", "fare ve klavye"),
    "telefon-chromium": ("Chromium, Android emülasyonu", "360 × 740 (testler 320-1024 arasında yeniden boyutlandırır)", "dokunma"),
    "telefon-webkit": ("WebKit, iOS emülasyonu", "390 × 664 (testler 320-1024 arasında yeniden boyutlandırır)", "dokunma"),
}

rows = []
def walk(suite, file=None):
    file = suite.get("file") or file
    for sp in suite.get("specs", []):
        for t in sp.get("tests", []):
            res = t.get("results", [])
            status = t.get("status")  # expected | unexpected | skipped | flaky
            ann = list(t.get("annotations") or [])
            for x in res: ann += list(x.get("annotations") or [])
            neden = next((a.get("description") or "" for a in ann if a.get("type") == "skip"), "")
            rows.append({"dosya": os.path.basename(sp.get("file") or file or ""), "baslik": sp["title"], "profil": t.get("projectName", ""), "durum": status,
                         "neden": neden, "olcum": [a.get("description") for a in ann if a.get("type") == "olcum"], "sure": sum(x.get("duration", 0) for x in res)})
    for s in suite.get("suites", []):
        walk(s, file)
for s in R.get("suites", []):
    walk(s)

DURUM = {"expected": "pass", "unexpected": "fail", "flaky": "fail"}
def durum(x):
    """Atlanan test, atlama gerekçesinin önekine göre sınıflanır: "not_run:" çalıştırılmadı, "not_applicable:" o profilde anlamsız."""
    if x["durum"] == "skipped":
        return "not_run" if x["neden"].startswith("not_run") else "not_applicable"
    return DURUM.get(x["durum"], x["durum"])
def say(items):
    c = collections.Counter(durum(x) for x in items)
    return c.get("pass", 0), c.get("fail", 0), c.get("not_run", 0), c.get("not_applicable", 0)

def versions():
    try:
        out = subprocess.run(["node", os.path.join(ROOT, "tools", "browser_versions.mjs")], capture_output=True, text=True, cwd=ROOT, timeout=120).stdout
        return json.loads(out.strip().splitlines()[-1])
    except Exception:
        return {}

V = versions()
pw = json.load(open(os.path.join(ROOT, "node_modules", "@playwright", "test", "package.json")))["version"]
axe = json.load(open(os.path.join(ROOT, "node_modules", "axe-core", "package.json")))["version"]
node = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
osname = "%s %s (%s)" % (platform.system().replace("Darwin", "macOS"), platform.mac_ver()[0] or platform.release(), platform.machine())
st = R.get("stats", {})
when = (st.get("startTime") or "")[:16].replace("T", " ")
p, f, nr, n = say(rows)
import hashlib
def icerik_ozeti():
    h = hashlib.sha256()
    for base in ("docs", "src"):
        for dp, _, fs in sorted(os.walk(os.path.join(ROOT, base))):
            for fn in sorted(fs):
                full = os.path.join(dp, fn)
                h.update(os.path.relpath(full, ROOT).encode()); h.update(open(full, "rb").read())
    return h.hexdigest()[:16]
def rev():
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        kirli = subprocess.run(["git", "status", "--porcelain", "--", "docs", "src", "tests", "tools"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        return r + (" (commit edilmemiş değişiklik var)" if kirli else "")
    except Exception:
        return "bilinmiyor"
L = []
L.append("# Test kanıt raporu\n")
L.append("Bu dosya `npm run rapor` ile son test koşusundan üretilir; elle düzenlenmez.\n")
L.append("| | |\n|---|---|")
L.append("| Koşu zamanı (UTC) | %s |" % (when or "bilinmiyor"))
L.append("| İşletim sistemi | %s |" % osname)
L.append("| Araçlar | Node %s, Playwright %s, axe-core %s, Python %s |" % (node, pw, axe, platform.python_version()))
L.append("| Motorlar | %s |" % ", ".join("%s %s" % (k, v) for k, v in V.items()) if V else "| Motorlar | okunamadı |")
L.append("| Komut | `npm test` (yerel sunucu `tools/serve.py`, site `/bpclaude/` yolu altında) |")
L.append("| Revizyon | %s |" % rev())
L.append("| docs/ ve src/ içerik özeti | `%s` (SHA-256, ilk 16 hane) |" % icerik_ozeti())
L.append("| Toplam | %d pass, %d fail, %d not_run, %d not_applicable; süre %.0f sn |\n" % (p, f, nr, n, (st.get("duration") or 0) / 1000.0))
L.append("`not_run`: araç desteği olmadığı ya da bilerek sınırlandığı için o profilde çalıştırılmayan denetim (ör. zorunlu renk emülasyonu yalnız Chromium'da var). `not_applicable`: o profilde anlamı olmayan test (ör. klavye denetimi dokunmatik profilde, dosya düzeyi denetim tek profilde). Gerekçeler test dosyalarında atlama açıklaması olarak yazılıdır.\n")

L.append("## Profil matrisi\n")
L.append("| Profil | Motor | Görünüm alanı | Giriş | pass | fail | not_run | not_applicable |\n|---|---|---|---|---:|---:|---:|---:|")
for prof, (motor, vp, giris) in PROFIL.items():
    it = [x for x in rows if x["profil"] == prof]
    if not it:
        L.append("| %s | %s | %s | %s | not_run | | | |" % (prof, motor, vp, giris)); continue
    a, b, c, d = say(it)
    L.append("| %s | %s | %s | %s | %d | %d | %d | %d |" % (prof, motor, vp, giris, a, b, c, d))
L.append("\nMotor sütunundaki emülasyon, gerçek cihaz değildir: dokunma, görünüm alanı ve kullanıcı aracısı taklit edilir.\n")

L.append("## Katmanlar\n")
L.append("| Katman | pass | fail | not_run | not_applicable |\n|---|---:|---:|---:|---:|")
for fn, ad in KATMAN.items():
    it = [x for x in rows if x["dosya"] == fn]
    if not it:
        L.append("| %s | not_run | | | |" % ad); continue
    a, b, c, d = say(it)
    L.append("| %s | %d | %d | %d | %d |" % (ad, a, b, c, d))

fails = [x for x in rows if durum(x) == "fail"]
olcum = sorted(set(m for x in rows for m in x["olcum"]))
if olcum:
    L.append("\n## Ölçümler\n")
    for m in olcum: L.append("- " + m)
nrun = collections.Counter("%s: %s" % (x["neden"].split(":", 1)[1].strip(), x["profil"]) for x in rows if durum(x) == "not_run")
if nrun:
    L.append("\n## Çalıştırılmayan denetimler (not_run)\n")
    for k, v in sorted(nrun.items()): L.append("- %s (%d test)" % (k, v))
L.append("\n## Başarısız testler\n")
if fails:
    for x in fails:
        L.append("- [%s] %s: %s" % (x["profil"], x["dosya"], x["baslik"]))
else:
    L.append("Yok.")

mp = os.path.join(ROOT, "qa", "manual.json")
if os.path.exists(mp):
    M = json.load(open(mp, encoding="utf-8"))
    L.append("\n## Otomatik koşmayan katmanlar\n")
    L.append("| Katman | Durum | Not |\n|---|---|---|")
    for x in M:
        L.append("| %s | %s | %s |" % (x["katman"], x["durum"], x["not"]))
pc = os.path.join(ROOT, "qa", "public_check.json")
if os.path.exists(pc):
    C = json.load(open(pc, encoding="utf-8"))
    L.append("\n## Yayın taraması\n")
    L.append("%d dosya tarandı (metin %d, çalışma kitabı %d, ikili %d); özel ad listesi %s (%d kural); ihlal %d." % (
        C["dosya"], C["taranan"]["metin"], C["taranan"]["xlsx"], C["taranan"]["ikili"], "yüklü" if C["ozel_liste"] else "yok", C["ozel_kural"], C["ihlal"]))
open(os.path.join(ROOT, "qa", "RAPOR.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("qa/RAPOR.md yazıldı: %d pass, %d fail, %d not_run, %d not_applicable" % (p, f, nr, n))
sys.exit(1 if f else 0)
