#!/usr/bin/env python3
"""openpyxl ile yazılmış formüllü bir çalışma kitabına hesaplanmış (önbellek) değerleri ekler.
Formüller aynen kalır; yalnız <v> öğeleri doldurulur. Böylece Quick Look, e-posta ve telefon
önizlemeleri de rakam gösterir. Kullanım: python3 add_cached_values.py <dosya.xlsx>"""
import os, re, shutil, sys, tempfile, warnings, zipfile
from xml.sax.saxutils import escape
warnings.filterwarnings("ignore")
import formulas, openpyxl

path = sys.argv[1]
xl = formulas.ExcelModel().loads(path).finish()
xl.calculate()
tmp = tempfile.mkdtemp()
xl.write(dirpath=tmp)
fn = [f for f in os.listdir(tmp) if f.lower().endswith(".xlsx")][0]
calc = openpyxl.load_workbook(os.path.join(tmp, fn))
vals = {ws.title.upper(): ws for ws in calc.worksheets}

zin = zipfile.ZipFile(path)
wbxml = zin.read("xl/workbook.xml").decode("utf-8")
rels = zin.read("xl/_rels/workbook.xml.rels").decode("utf-8")
rid2target = {}
for m in re.finditer(r"<Relationship [^>]*>", rels):
    tag = m.group(0)
    rid = re.search(r'Id="([^"]+)"', tag).group(1); tgt = re.search(r'Target="([^"]+)"', tag).group(1)
    rid2target[rid] = tgt.lstrip("/") if tgt.startswith("/") else "xl/" + tgt
sheetfile = {}
for m in re.finditer(r"<sheet [^>]*>", wbxml):
    tag = m.group(0)
    name = re.search(r'name="([^"]+)"', tag).group(1); rid = re.search(r'r:id="([^"]+)"', tag).group(1)
    sheetfile[rid2target[rid]] = name

cell_re = re.compile(r'<c r="([A-Z]+[0-9]+)"([^>]*)>(<f>.*?</f>)<v>\s*</v></c>|<c r="([A-Z]+[0-9]+)"([^>]*)>(<f>.*?</f>)<v/></c>', re.S)
stats = {"num": 0, "str": 0, "bool": 0, "err": 0, "empty": 0}
def fill(name):
    ws = vals[name.upper()]
    def rep(m):
        coord = m.group(1) or m.group(4); attrs = m.group(2) if m.group(1) else m.group(5); f = m.group(3) or m.group(6)
        v = ws[coord].value
        attrs = re.sub(r'\s+t="[^"]*"', "", attrs or "")
        if v is None or v == "":
            stats["empty"] += 1
            return f'<c r="{coord}"{attrs} t="str">{f}<v></v></c>'
        if isinstance(v, bool):
            stats["bool"] += 1
            return f'<c r="{coord}"{attrs} t="b">{f}<v>{int(v)}</v></c>'
        if isinstance(v, (int, float)):
            stats["num"] += 1
            return f'<c r="{coord}"{attrs}>{f}<v>{repr(float(v)) if isinstance(v, float) else v}</v></c>'
        sv = str(v)
        if sv.startswith("#"):
            stats["err"] += 1
            return f'<c r="{coord}"{attrs} t="e">{f}<v>{escape(sv)}</v></c>'
        stats["str"] += 1
        return f'<c r="{coord}"{attrs} t="str">{f}<v>{escape(sv)}</v></c>'
    return rep

out = path + ".tmp"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename in sheetfile:
            xml = data.decode("utf-8")
            xml = cell_re.sub(fill(sheetfile[item.filename]), xml)
            data = xml.encode("utf-8")
        elif item.filename == "xl/workbook.xml":
            xml = data.decode("utf-8")
            if "<calcPr" not in xml:
                xml = xml.replace("</workbook>", '<calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>')
            data = xml.encode("utf-8")
        zout.writestr(item, data)
zin.close()
shutil.move(out, path)
# doğrulama
a = openpyxl.load_workbook(path); b = openpyxl.load_workbook(path, data_only=True)
nf = filled = 0
for ws in a.worksheets:
    wb2 = b[ws.title]
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("="):
                nf += 1
                if wb2[c.coordinate].value is not None: filled += 1
print(f"{os.path.basename(path)}: formül {nf}, önbellekli {filled}, dağılım {stats}")
sys.exit(0 if stats["err"] == 0 and filled >= nf - stats["empty"] else 1)
