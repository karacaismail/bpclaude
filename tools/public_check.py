#!/usr/bin/env python3
"""Yayın öncesi güvenlik taraması. Depoya girecek her dosyayı (yalnız docs/ değil) yasaklı ifade listesiyle tarar.

Depo herkese açık olduğu için kural şudur: Git'e girecek hiçbir dosyada kişi adı, müşteri ya da üçüncü taraf adı,
yerel dosya yolu, e-posta, IP adresi, anahtar ya da gizli değer bulunmaz. Özel ad listesi depoda tutulmaz
(private/forbidden_terms.json, .gitignore içinde); liste yoksa tarama eksik sayılır ve betik hata verir.

Kullanım: python3 tools/public_check.py [--allow-missing-private] [--json qa/public_check.json]
Çıkış kodu: 0 temiz, 1 ihlal var, 2 özel liste yok."""
import json, os, re, subprocess, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import forbidden

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_EXT = (".html", ".css", ".js", ".mjs", ".json", ".csv", ".txt", ".md", ".py", ".xml", ".svg", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".sh", ".gitignore", ".nojekyll", ".lock")
BINARY_OK = (".png", ".jpg", ".jpeg", ".webp", ".ico", ".woff2")
# Tarayıcının kendi desen kaynakları kendisiyle eşleşir; bu dosyalar elle gözden geçirilir.
SELF = {"tools/forbidden.py"}
# Yerel geliştirme adresi ve belge örnekleri: IP deseninin bilinen zararsız eşleşmeleri.
ALLOW = [re.compile(r"^127\.0\.0\.1$"), re.compile(r"^0\.0\.0\.0$")]
EXT_URL = re.compile(r"""(?:href|src|action|srcset|poster|data)\s*=\s*["']\s*(?:https?:)?//[^"']+|url\(\s*["']?(?:https?:)?//""", re.I)
FORBIDDEN_NAMES = re.compile(r"(^|/)(\.env(\..*)?|id_rsa|id_ed25519|.*\.pem|.*\.p12|.*\.key|.*\.sqlite3?|.*\.bak|.*\.dump)$", re.I)


def tracked_files():
    """Git'e girecek dosyalar: izlenenler ve izlenmeyip yok sayılmayanlar."""
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files", "-co", "--exclude-standard", "-z"], capture_output=True, check=True).stdout
        files = [f for f in out.decode("utf-8").split("\0") if f]
        if files:
            return sorted(files), "git"
    except Exception:
        pass
    skip = {"node_modules", ".git", "private", "test-results", "playwright-report", "__pycache__"}
    files = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip]
        for n in names:
            files.append(os.path.relpath(os.path.join(base, n), ROOT))
    return sorted(files), "walk"


def scan_text(rel, text, hits):
    for why, word, ctx in forbidden.scan(text):
        if any(rx.match(word) for rx in ALLOW):
            continue
        hits.append({"dosya": rel, "tur": why, "ifade": word, "cevre": ctx[:140]})


def main():
    args = sys.argv[1:]
    allow_missing = "--allow-missing-private" in args
    out_json = args[args.index("--json") + 1] if "--json" in args else None
    files, source = tracked_files()
    hits, skipped, counts = [], [], {"metin": 0, "xlsx": 0, "ikili": 0}
    for rel in files:
        full = os.path.join(ROOT, rel)
        if not os.path.isfile(full):
            continue
        if FORBIDDEN_NAMES.search(rel):
            hits.append({"dosya": rel, "tur": "yayımlanmaması gereken dosya türü", "ifade": os.path.basename(rel), "cevre": ""})
        # dosya adının kendisi de taranır
        scan_text(rel, rel, hits)
        if rel in SELF:
            skipped.append(rel)
            continue
        low = rel.lower()
        if low.endswith(".xlsx"):
            counts["xlsx"] += 1
            with zipfile.ZipFile(full) as z:
                for name in z.namelist():
                    if name.endswith((".xml", ".rels")):
                        scan_text("%s!%s" % (rel, name), z.read(name).decode("utf-8", "replace"), hits)
            continue
        if low.endswith(BINARY_OK):
            counts["ikili"] += 1
            continue
        try:
            text = open(full, encoding="utf-8").read()
        except UnicodeDecodeError:
            hits.append({"dosya": rel, "tur": "taranamayan ikili dosya", "ifade": "", "cevre": ""})
            continue
        counts["metin"] += 1
        scan_text(rel, text, hits)
        if rel.startswith("docs/") and low.endswith((".html", ".css")):
            for m in EXT_URL.finditer(text):
                hits.append({"dosya": rel, "tur": "dış kaynağa bağlantı", "ifade": m.group(0)[:80], "cevre": ""})
            if low.endswith(".html") and 'name="robots" content="noindex' not in text:
                hits.append({"dosya": rel, "tur": "noindex etiketi eksik", "ifade": "", "cevre": ""})
    robots = os.path.join(ROOT, "docs", "robots.txt")
    if not (os.path.isfile(robots) and "Disallow: /" in open(robots).read()):
        hits.append({"dosya": "docs/robots.txt", "tur": "robots.txt eksik ya da açık", "ifade": "", "cevre": ""})
    result = {"kaynak": source, "dosya": len(files), "taranan": counts, "ozel_liste": forbidden.PRIVATE_LOADED, "ozel_kural": forbidden.PRIVATE_COUNT,
              "elle_gozden_gecirilen": skipped, "ihlal": len(hits), "ihlaller": hits[:200]}
    if out_json:
        os.makedirs(os.path.dirname(os.path.join(ROOT, out_json)), exist_ok=True)
        json.dump({k: v for k, v in result.items() if k != "ihlaller"}, open(os.path.join(ROOT, out_json), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for h in hits[:60]:
        print("%s: %s: '%s' … %s" % (h["dosya"], h["tur"], h["ifade"], h["cevre"]))
    print("yayın taraması: %d dosya (%s), metin %d, xlsx %d, ikili %d; özel liste %s (%d kural); ihlal %d" % (
        len(files), source, counts["metin"], counts["xlsx"], counts["ikili"], "yüklü" if forbidden.PRIVATE_LOADED else "YOK", forbidden.PRIVATE_COUNT, len(hits)))
    if hits:
        return 1
    if not forbidden.PRIVATE_LOADED and not allow_missing:
        print("özel ad listesi yok: tarama eksik. Listeyi private/forbidden_terms.json yoluna koyun ya da --allow-missing-private verin.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
