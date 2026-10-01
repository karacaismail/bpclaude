"""Kamuya açık yayına girmemesi gereken ifadeler. Ajan çıktıları, derlenmiş site ve depoya girecek bütün dosyalar bu listeyle taranır.

İki katman vardır:
- Genel desenler (aşağıda): yerel dosya yolu, IP adresi, e-posta, anahtar ve token biçimleri. Bunlar ad içermez, depoda durur.
- Özel desenler: kişi, müşteri ve üçüncü taraf adları. Listenin kendisi de sızıntı olacağı için depoda tutulmaz;
  private/forbidden_terms.json dosyasından okunur ([desen, büyük-küçük harf duyarlı mı, açıklama] üçlüleri).
  Dosya yoksa PRIVATE_LOADED False olur ve yayın taraması eksik sayılır."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVATE_FILE = os.path.join(ROOT, "private", "forbidden_terms.json")

# (desen, büyük-küçük harf duyarlı mı, açıklama)
GENERIC = [
    (r"/Users/[^/\s\"']+|/home/[^/\s\"']+|[A-Za-z]:\\Users\\", False, "yerel dosya yolu"),
    (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", False, "IP adresi"),
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", False, "e-posta adresi"),
    (r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|\bsk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----", True, "anahtar ya da token"),
]

PRIVATE = []
if os.path.isfile(PRIVATE_FILE):
    PRIVATE = [tuple(x) for x in json.load(open(PRIVATE_FILE, encoding="utf-8"))]
PRIVATE_LOADED = bool(PRIVATE)
PRIVATE_COUNT = len(PRIVATE)
RULES = GENERIC + PRIVATE
COMPILED = [(re.compile(p, 0 if cs else re.I), why, p) for p, cs, why in RULES]


def scan(text):
    """Bulunan ihlalleri (açıklama, eşleşen metin, çevresi) listesi olarak döndürür."""
    hits = []
    for rx, why, _ in COMPILED:
        for m in rx.finditer(text):
            a, b = max(0, m.start() - 40), min(len(text), m.end() + 40)
            hits.append((why, m.group(0), text[a:b].replace("\n", " ")))
    return hits


if __name__ == "__main__":
    import sys
    bad = 0
    for path in sys.argv[1:]:
        for why, word, ctx in scan(open(path, encoding="utf-8").read()):
            bad += 1
            print(f"{path}: {why}: '{word}' … {ctx}")
    print("ihlal:", bad, "| özel liste:", "yüklü" if PRIVATE_LOADED else "YOK")
    sys.exit(1 if bad else 0)
