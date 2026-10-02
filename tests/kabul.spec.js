// Kabul ölçütleri: bağımsız tasarım incelemesinde bulunan kusurların geri gelmesini yakalar.
// Her test, incelemedeki bir bulgunun ölçülebilir karşılığıdır (ilk ekranda içerik, satır yüksekliği, renk ve biçim ayrımı, tutarlılık).
import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { DOCS, isPhoneProject } from "./helpers.js";

/** Bir tokenın, verilen öğenin bağlamında çözülmüş rengini rgb() olarak verir. */
async function tokenRgb(locator, name) {
  return locator.evaluate((el, n) => {
    const probe = document.createElement("span");
    probe.style.color = getComputedStyle(el).getPropertyValue(n).trim();
    el.appendChild(probe);
    const c = getComputedStyle(probe).color;
    probe.remove();
    return c;
  }, name);
}

test.describe("karar ekranı: ilk ekranda seçenek görünür", () => {
  test("390×844: ilk satırın başlığı, kararı, puanı ve nakit değeri ilk ekranda", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("siralama.html");
    const row = page.locator("#liste > li").first();
    for (const sel of [".opt__title a", ".tag", ".metric--score .metric__val", ".metric--cash .metric__val"]) {
      const b = await row.locator(sel).first().evaluate((el) => el.getBoundingClientRect().bottom);
      expect(b, `${sel} ilk ekranda`).toBeLessThanOrEqual(844);
    }
  });

  test("390×664 (tarayıcı çubukları açıkken) ve 320×568: ilk satırın başlığı ve kararı ilk ekranda", async ({ page }) => {
    for (const [w, h] of [[390, 664], [320, 568]]) {
      await page.setViewportSize({ width: w, height: h });
      await page.goto("siralama.html");
      const row = page.locator("#liste > li").first();
      const baslik = await row.locator(".opt__title a").evaluate((el) => el.getBoundingClientRect().top);
      expect(baslik, `${w}×${h}: ilk satırın başlığı ilk ekranda başlar`).toBeLessThan(h - 24);
      if (h >= 664) {
        const karar = await row.locator(".tag").first().evaluate((el) => el.getBoundingClientRect().bottom);
        expect(karar, `${w}×${h}: karar etiketi ilk ekranda`).toBeLessThanOrEqual(h);
      }
    }
  });

  test("1280×800: ilk üç satır tam olarak ilk ekranda, süzgeç paneli kapalı başlar ve sütunlar aynı çizgide", async ({ page }, info) => {
    test.skip(isPhoneProject(info.project.name), "not_applicable: geniş ekran denetimi masaüstü motorlarında yapılır");
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("siralama.html");
    expect(await page.locator("#suzgec-panel").evaluate((el) => el.open), "süzgeç paneli kapalı").toBe(false);
    const b = await page.locator("#liste > li").nth(2).evaluate((el) => el.getBoundingClientRect().bottom);
    expect(b, "üçüncü satırın alt kenarı ilk ekranda").toBeLessThanOrEqual(800);
    // Sayfa başındaki dağılım, süzgeç bölümü ve satırlardaki ölçü sütunu her geniş ekran genişliğinde aynı dikey çizgide başlar.
    for (const w of [1000, 1024, 1280, 1600]) {
      await page.setViewportSize({ width: w, height: 800 });
      const x = await page.evaluate(() => [".page-head__fig", "#suzgec-panel", "#liste > li .opt__metrics"].map((s) => document.querySelector(s).getBoundingClientRect().left));
      expect(Math.max(...x) - Math.min(...x), `${w}: sol kenarlar ${x.map((v) => v.toFixed(1)).join(", ")}`).toBeLessThanOrEqual(1);
    }
  });

  for (const [w, sinir] of [[320, 450], [390, 390]]) {
    test(`satır yüksekliği bütçesi: ${w} genişlikte ortanca satır en çok ${sinir} px`, async ({ page }) => {
      await page.setViewportSize({ width: w, height: 800 });
      await page.goto("siralama.html");
      const hs = await page.locator("#liste > li").evaluateAll((els) => els.map((x) => x.getBoundingClientRect().height).sort((a, b) => a - b));
      const ortanca = hs[Math.floor(hs.length / 2)];
      expect(ortanca, `ortanca satır yüksekliği (en uzun ${Math.round(hs[hs.length - 1])})`).toBeLessThanOrEqual(sinir);
    });
  }

  test("320 genişlikte karar dağılımı adları sözcük ortasından bölünmez", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("siralama.html");
    // Her sözcük tek bir satır kutusunda durmalı: sözcüğün aralığı birden çok dikdörtgene bölünüyorsa sözcük ortasından kırılmıştır.
    const bolunen = await page.locator(".dist-legend__ad").evaluateAll((els) => {
      const out = [];
      for (const el of els) {
        const node = el.firstChild, text = node.textContent;
        for (const m of text.matchAll(/\S+/g)) {
          const r = document.createRange();
          r.setStart(node, m.index); r.setEnd(node, m.index + m[0].length);
          const satir = new Set([...r.getClientRects()].map((x) => Math.round(x.top)));
          if (satir.size > 1) out.push(m[0]);
        }
      }
      return out;
    });
    expect(await page.locator(".dist-legend__ad").count()).toBeGreaterThan(2);
    expect(bolunen, "ortasından bölünen sözcük").toEqual([]);
  });

  test("geniş ekranda satır metinleri kırılmaz: karar ve kapı özeti tek satır, nakit aralığı tek satır", async ({ page }, info) => {
    test.skip(isPhoneProject(info.project.name), "not_applicable: geniş ekran denetimi masaüstü motorlarında yapılır");
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("siralama.html");
    const r = await page.locator("#liste > li").evaluateAll((rows) => {
      const lines = (el) => Math.round(el.getBoundingClientRect().height / parseFloat(getComputedStyle(el).lineHeight));
      let etiket = 0, alt = 0;
      for (const row of rows) {
        const kids = [...row.querySelector(".opt__tags").children];
        if (kids.length > 1 && kids[kids.length - 1].getBoundingClientRect().top >= kids[0].getBoundingClientRect().bottom) etiket++;
        for (const s of row.querySelectorAll(".metric__sub")) if (lines(s) > 1) alt++;
      }
      return { etiket, alt };
    });
    expect(r).toEqual({ etiket: 0, alt: 0 });
  });
});

test.describe("renk ve biçim ayrımı", () => {
  test("kapıda kaldı kararı nötr mürekkep rengindedir; marka turuncusu yalnız öne çıkan karardadır", async ({ page }) => {
    await page.goto("siralama.html");
    const kaldi = page.locator('.dist__seg[data-karar="kapida-kaldi"]');
    const test1 = page.locator('.dist__seg[data-karar="once-test-et"]');
    expect(await kaldi.evaluate((el) => getComputedStyle(el).backgroundColor)).toBe(await tokenRgb(kaldi, "--c-ink"));
    expect(await test1.evaluate((el) => getComputedStyle(el).backgroundColor)).toBe(await tokenRgb(test1, "--c-brand"));
    const etiket = page.locator('#liste .tag[data-karar="kapida-kaldi"]').first();
    expect(await etiket.evaluate((el) => getComputedStyle(el).color)).toBe(await tokenRgb(etiket, "--c-ink"));
  });

  test("nakit çizgisi: eksi değer içi boş halka, artı değer dolu nokta", async ({ page }) => {
    await page.goto("siralama.html");
    const eksi = page.locator('#liste .range[data-isaret="eksi"] .range__dot').first();
    const arti = page.locator('#liste .range[data-isaret="arti"] .range__dot').first();
    const e = await eksi.evaluate((el) => { const s = getComputedStyle(el); return { bg: s.backgroundColor, bw: parseFloat(s.borderTopWidth) }; });
    const a = await arti.evaluate((el) => getComputedStyle(el).backgroundColor);
    expect(e.bg, "eksi nokta zemin renginde").toBe(await tokenRgb(eksi, "--c-paper"));
    expect(e.bw, "eksi nokta kenarlıklı").toBeGreaterThanOrEqual(2);
    expect(a, "artı nokta dolu").toBe(await tokenRgb(arti, "--c-ink"));
  });

  test("nakit çizgisi: çentikler izin üstüne ve altına eşit taşar, nokta üstte çizilir ve çentiğin iki ucu noktanın dışından görünür", async ({ page }) => {
    await page.goto("siralama.html");
    const m = await page.locator("#liste .range:has(.range__dot)").first().evaluate((el) => {
      const kids = [...el.children].map((c) => c.className);
      const r = (s) => el.querySelector(s).getBoundingClientRect();
      const iz = getComputedStyle(el, "::before");
      const kutu = el.getBoundingClientRect();
      return { kids, dot: r(".range__dot"), zero: r(".range__zero"), target: r(".range__target"), izUst: kutu.top + parseFloat(iz.top), izAlt: kutu.top + parseFloat(iz.top) + parseFloat(iz.height) };
    });
    expect(m.kids.indexOf("range__dot"), "nokta çentiklerden sonra (üstte) gelir").toBeGreaterThan(m.kids.indexOf("range__zero"));
    expect(m.kids.indexOf("range__dot")).toBeGreaterThan(m.kids.indexOf("range__target"));
    for (const c of [m.zero, m.target]) {
      const ust = m.izUst - c.top, alt = c.bottom - m.izAlt;
      expect(Math.abs(ust - alt), "çentik izin üstüne ve altına eşit taşar").toBeLessThanOrEqual(1);
      expect(m.dot.top - c.top, "çentiğin üst ucu noktanın halesinin dışında").toBeGreaterThanOrEqual(3);
      expect(c.bottom - m.dot.bottom, "çentiğin alt ucu noktanın halesinin dışında").toBeGreaterThanOrEqual(3);
    }
    // Puan çubuğu ile nakit izi aynı kalınlıkta ve (yan yana durdukları geniş ekranda) aynı yükseklikte.
    await page.setViewportSize({ width: 1280, height: 800 });
    const hiza = await page.locator("#liste > li").first().evaluate((row) => {
      const meter = row.querySelector(".metric--score .meter").getBoundingClientRect();
      const range = row.querySelector(".range"), iz = getComputedStyle(range, "::before"), kutu = range.getBoundingClientRect();
      return { meterUst: meter.top, meterH: meter.height, izUst: kutu.top + parseFloat(iz.top), izH: parseFloat(iz.height) };
    });
    expect(Math.abs(hiza.meterH - hiza.izH), "çubuk ve iz aynı kalınlıkta").toBeLessThanOrEqual(0.5);
    expect(Math.abs(hiza.meterUst - hiza.izUst), "çubuk ve iz aynı yükseklikte").toBeLessThanOrEqual(1);
  });

  test("nakit çizgisi: taşma oku, ölçek dışı baz değer ve dar aralık model verisiyle satır satır tutarlı", async ({ page }) => {
    // Beklenen durum yayımlanan model dosyasından hesaplanır: eksen hedefin −0,5 ile 1,5 katı arasıdır (yüzde 0 ile 100).
    const model = JSON.parse(fs.readFileSync(path.join(DOCS, "indir", "bpclaude-model.json"), "utf8"));
    const beklenen = {};
    for (const o of model.secenekler) {
      const f = o.finans, v = [f.kotu.net_nakit, f.baz.net_nakit, f.iyi.net_nakit].map((x) => (x / f.hedef_tl + 0.5) / 2);
      const lo = Math.min(...v), hi = Math.max(...v), baz = v[1];
      const tasma = [lo < 0 ? "sol" : "", hi > 1 ? "sag" : ""].filter(Boolean).join(" ");
      const kis = (x) => Math.min(1, Math.max(0, x)) * 100;
      const nokta = !(baz < 0 || baz > 1);
      // Tarama kırıntısı kuralı tools/sitelib.py ile aynıdır: noktanın halesi yüzde 4,5; bir yanda yüzde 5'ten kısa kalan parça çizilmez.
      let a = kis(lo), z = kis(hi);
      const b = kis(baz);
      if (nokta) {
        if (!tasma.includes("sol") && (b - 4.5) - a < 5) a = b;
        if (!tasma.includes("sag") && z - (b + 4.5) < 5) z = b;
      }
      beklenen["row-" + o.id] = { tasma, nokta, tarama: !!tasma || z - a > 0 };
    }
    await page.goto("siralama.html");
    const gercek = await page.locator("#liste > li").evaluateAll((rows) => Object.fromEntries(rows.map((row) => {
      const el = row.querySelector(".range"), span = el.querySelector(".range__span");
      const ok = (ps) => { if (!span) return false; const s = getComputedStyle(span, ps); return s.content !== "none" && parseFloat(s.width) > 0; };
      return [row.id, { tasma: el.dataset.tasma || "", nokta: !!el.querySelector(".range__dot"), tarama: !!span, sag: ok("::after"), sol: ok("::before") }];
    })));
    expect(Object.keys(gercek).length).toBe(model.secenekler.length);
    const fark = Object.entries(gercek).filter(([id, g]) => {
      const b = beklenen[id];
      return g.tasma !== b.tasma || g.nokta !== b.nokta || g.tarama !== b.tarama || g.sag !== b.tasma.includes("sag") || g.sol !== b.tasma.includes("sol");
    }).map(([id, g]) => `${id}: beklenen ${JSON.stringify(beklenen[id])}, bulunan ${JSON.stringify(g)}`);
    expect(fark).toEqual([]);
    const b = Object.values(beklenen);
    expect(b.filter((x) => x.tasma.includes("sag")).length, "en az bir satır ölçeği sağdan aşıyor").toBeGreaterThan(0);
    expect(b.filter((x) => x.tasma === "").length, "aşmayan satırlar da var").toBeGreaterThan(0);
    expect(b.filter((x) => !x.nokta).length, "baz değeri ölçek dışında kalan satır var").toBeGreaterThan(0);
    expect(b.filter((x) => !x.tarama).length, "aralığı taranmayacak kadar dar satır var").toBeGreaterThan(0);
  });

  test("proje başındaki nakit çizgisinde sıfır ve hedef gerçek metinle, çentiğin altında yazar", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("proje/qral.html");
    const m = await page.locator(".masthead .metric--cash").evaluate((el) => {
      const c = (s) => { const r = el.querySelector(s).getBoundingClientRect(); return r.left + r.width / 2; };
      const [sifir, hedef] = [...el.querySelectorAll(".range__axis span")];
      const mid = (x) => { const r = x.getBoundingClientRect(); return r.left + r.width / 2; };
      return { sifir: sifir.textContent, hedef: hedef.textContent, dx0: Math.abs(mid(sifir) - c(".range__zero")), dxh: Math.abs(mid(hedef) - c(".range__target")), fs: parseFloat(getComputedStyle(sifir).fontSize) };
    });
    expect(m.sifir).toBe("0");
    expect(m.hedef).toMatch(/^hedef ₺/);
    expect(m.dx0, "sıfır yazısı çentiğin altında").toBeLessThan(2);
    expect(m.dxh, "hedef yazısı çentiğin altında").toBeLessThan(2);
    expect(m.fs).toBeGreaterThanOrEqual(12.9);
  });

  test("grafik izi zeminden ayrışır: açık zeminde ve koyu kapakta", async ({ page }) => {
    await page.goto("siralama.html");
    const lum = (rgb) => {
      const [r, g, b] = rgb.match(/[\d.]+/g).slice(0, 3).map((v) => { const s = Number(v) / 255; return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4); });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };
    const body = page.locator("body");
    expect(await body.evaluate((el) => getComputedStyle(el).getPropertyValue("--c-track").trim()), "iz tokenı tanımlı").not.toBe("");
    // Çizili izin kendi rengi ölçülür (token adı değil): kâğıtta en az 1,3:1, bantta en az 1,2:1.
    const iz = await page.locator("#liste .meter").first().evaluate((el) => getComputedStyle(el).backgroundColor);
    for (const [zemin, en] of [["--c-paper", 1.3], ["--c-band", 1.2]]) {
      const a = lum(iz), b = lum(await tokenRgb(body, zemin));
      const oran = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
      expect(oran, `iz ile ${zemin} karşıtlığı`).toBeGreaterThanOrEqual(en);
    }
    await page.goto("index.html");
    const bar = page.locator(".cover .funnel__bar").first();
    const a = lum(await bar.evaluate((el) => getComputedStyle(el).backgroundColor)), b = lum(await bar.evaluate((el) => getComputedStyle(el.closest(".cover")).backgroundColor));
    expect((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05), "kapakta iz ile zemin karşıtlığı").toBeGreaterThanOrEqual(1.3);
  });
});

test.describe("özet sayfası", () => {
  test("kısa yanıt hedef tutarını söyler ve hunide sonuç satırları öne çıkar", async ({ page }) => {
    await page.goto("index.html");
    await expect(page.locator(".cover__answer")).toContainText("3.000 USD");
    const key = page.locator(".funnel__row--key .funnel__num").first();
    const normal = page.locator(".funnel__row:not(.funnel__row--key) .funnel__num").first();
    const k = await key.evaluate((el) => { const s = getComputedStyle(el); return { c: s.color, fs: parseFloat(s.fontSize) }; });
    const n = await normal.evaluate((el) => { const s = getComputedStyle(el); return { c: s.color, fs: parseFloat(s.fontSize) }; });
    expect(k.c, "sonuç satırı sayısı vurgu renginde").toBe(await tokenRgb(key, "--c-brand"));
    expect(k.fs, "sonuç satırı sayısı daha büyük").toBeGreaterThan(n.fs);
    const dolgu = await page.locator(".funnel__row:not(.funnel__row--key) .funnel__fill").first().evaluate((el) => getComputedStyle(el).backgroundColor);
    expect(dolgu, "eleme satırlarının dolgusu kısık").not.toBe(await tokenRgb(normal, "--c-ink"));
  });

  test("390×844: huninin sonuç satırı ilk ekranda", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("index.html");
    const b = await page.locator(".funnel__row--key").first().evaluate((el) => el.getBoundingClientRect().bottom);
    expect(b).toBeLessThanOrEqual(844);
  });
});

test.describe("tutarlılık", () => {
  test("proje sözlüğü 390×844: arama ve harf gezintisi ilk ekranda, yanıt kalıbı listenin altında", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("projeler.html");
    await expect(page.locator("#sq")).toBeVisible();
    const ara = await page.locator("#sq").evaluate((el) => el.getBoundingClientRect().bottom);
    expect(ara, "arama alanı ilk ekranda").toBeLessThanOrEqual(844);
    const az = await page.locator(".az").evaluate((el) => el.getBoundingClientRect().top);
    expect(az, "harf gezintisi ilk ekranda başlar").toBeLessThan(844);
    const ad = await page.locator(".glossary__name").first().evaluate((el) => el.getBoundingClientRect().bottom);
    expect(ad, "ilk proje adı ilk ekranda").toBeLessThanOrEqual(844);
    const sira = await page.evaluate(() => {
      const liste = document.getElementById("sozluk-liste"), kalip = document.getElementById("nasil-anlatilir");
      return !!(liste.compareDocumentPosition(kalip) & Node.DOCUMENT_POSITION_FOLLOWING);
    });
    expect(sira, "yanıt kalıbı listeden sonra gelir").toBe(true);
  });

  test("proje sözlüğü geniş ekranda sürekli iki sütuna akar; tür adı her zaman adın altında", async ({ page }, info) => {
    test.skip(isPhoneProject(info.project.name), "not_applicable: geniş ekran denetimi masaüstü motorlarında yapılır");
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("projeler.html");
    const m = await page.locator("#sozluk-liste").evaluate((box) => {
      const kutu = box.getBoundingClientRect(), orta = kutu.left + kutu.width / 2;
      const items = [...box.querySelectorAll(".glossary > li")].map((li) => li.getBoundingClientRect());
      const sol = items.filter((r) => r.left < orta), sag = items.filter((r) => r.left >= orta);
      const yan = [...box.querySelectorAll(".glossary__link")].filter((a) => a.querySelector(".glossary__type").getBoundingClientRect().top < a.querySelector(".glossary__name").getBoundingClientRect().bottom - 1).length;
      return { sol: sol.length, sag: sag.length, fark: Math.abs(Math.max(...sol.map((r) => r.bottom)) - Math.max(...sag.map((r) => r.bottom))), yan };
    });
    expect(m.sol + m.sag).toBe(45);
    expect(Math.abs(m.sol - m.sag), `sütunlardaki girdi sayısı: ${m.sol} ve ${m.sag}`).toBeLessThanOrEqual(8);
    expect(m.fark, "iki sütunun alt kenarları arasındaki fark").toBeLessThanOrEqual(400);
    expect(m.yan, "tür adı başlığın yanında duran girdi").toBe(0);
  });

  test("yöntem katmanları kart değil: zeminsiz, numaraları çizgiyle bağlı adımlar", async ({ page }) => {
    for (const url of ["sablon.html", "index.html"]) {
      await page.goto(url);
      const a = page.locator(".layers a").first();
      expect(await a.evaluate((el) => getComputedStyle(el).backgroundColor), `${url}: adım zeminsiz`).toBe("rgba(0, 0, 0, 0)");
      const bag = await page.locator(".layers li").first().evaluate((el) => { const s = getComputedStyle(el, "::after"); return { c: s.content, w: parseFloat(s.width), h: parseFloat(s.height) }; });
      expect(bag.c, `${url}: bağlantı çizgisi var`).not.toBe("none");
      expect(Math.max(bag.w, bag.h)).toBeGreaterThan(8);
    }
  });

  test("bölüm gezintisi her sayfada aynı desen: şablon da yapışkan hap gezintisi kullanır", async ({ page }) => {
    await page.goto("sablon.html");
    await expect(page.locator(".toc .toc__list a")).not.toHaveCount(0);
    await expect(page.locator(".anchor-nav")).toHaveCount(0);
  });

  test("numaralı adım daireleri sayfalar arasında aynı", async ({ page }) => {
    await page.goto("projeler.html");
    const f = await page.locator(".formula > li").first().evaluate((el) => { const s = getComputedStyle(el, "::before"); return [s.backgroundColor, s.color]; });
    await page.goto("proje/qral.html");
    const s = await page.locator("#nedir .steps > li").first().evaluate((el) => { const x = getComputedStyle(el, "::before"); return [x.backgroundColor, x.color]; });
    await page.goto("sablon.html");
    const l = await page.locator(".layers a").first().evaluate((el) => { const x = getComputedStyle(el, "::before"); return [x.backgroundColor, x.color]; });
    expect(s).toEqual(f);
    expect(l).toEqual(f);
  });

  test("işaretler açıklaması açılır bölümde, üç grup halinde ve ekran okuyucuya açık", async ({ page }) => {
    await page.goto("siralama.html");
    const d = page.locator("details.howto");
    await expect(d).toHaveCount(1);
    await expect(d.locator(".legend__group")).toHaveCount(3);
    expect(await d.locator(".legend").getAttribute("aria-hidden")).toBeNull();
    await d.locator("summary").click();
    await expect(d.locator(".legend")).toBeVisible();
  });

  test("proje başı: üst etiket tek satır, ölçüler satırdaki ölçü bileşeniyle aynı", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("proje/qral.html");
    const eb = await page.locator(".masthead .eyebrow").evaluate((el) => el.getBoundingClientRect().height / parseFloat(getComputedStyle(el).lineHeight));
    expect(Math.round(eb), "üst etiket satır sayısı").toBe(1);
    await expect(page.locator(".masthead .subtitle")).toHaveCount(0);
    await expect(page.locator(".keyfacts .metric--score .metric__val")).toBeVisible();
    await expect(page.locator(".keyfacts .metric--cash .metric__val")).toBeVisible();
    const h = await page.locator(".keyfacts .metric--best a").evaluate((el) => el.getBoundingClientRect().height);
    expect(h, "en iyi seçenek bağlantısı dokunma hedefi boyunda").toBeGreaterThanOrEqual(43.5);
  });
});

test.describe("gezinme şeridi kenar ipuçları", () => {
  test("şerit kaydıkça solma kenarı konuma göre değişir", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("index.html");
    const list = page.locator("#site-nav-list");
    await expect(list).toHaveAttribute("data-kenar", "bas");
    await list.evaluate((el) => { el.scrollLeft = Math.round((el.scrollWidth - el.clientWidth) / 2); });
    await expect(list).toHaveAttribute("data-kenar", "orta");
    const maske = () => list.evaluate((el) => getComputedStyle(el).maskImage || getComputedStyle(el).webkitMaskImage);
    const orta = await maske();
    await list.evaluate((el) => { el.scrollLeft = el.scrollWidth; });
    await expect(list).toHaveAttribute("data-kenar", "son");
    const son = await maske();
    await list.evaluate((el) => { el.scrollLeft = 0; });
    await expect(list).toHaveAttribute("data-kenar", "bas");
    const bas = await maske();
    expect(new Set([bas, orta, son]).size, "üç konumun maskesi birbirinden farklı").toBe(3);
    for (const m of [bas, orta, son]) expect(m).toContain("gradient");
  });
});

test.describe("gezinme şeridi: fare, dokunma ve geri yönde klavye", () => {
  test("solma bölgesinde yarısı görünen bağlantıya ilk tıklama sayfayı açar", async ({ page }, info) => {
    // Bağlantı işaretçiyle odaklanınca şerit kaydırılmamalı: kaydırılırsa bağlantı işaretçinin altından kaçar ve tıklama boşa gider.
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("index.html");
    const hedef = await page.locator("#site-nav-list a").evaluateAll((els) => {
      const vw = document.documentElement.clientWidth;
      const el = els.find((a) => { const r = a.getBoundingClientRect(); return r.left < vw - 12 && r.right > vw - 40; });
      const r = el.getBoundingClientRect();
      // Bağlantının görünen kısmının en sağına basılır: şerit kaydırılsaydı tam bu nokta bağlantının dışında kalırdı.
      return { href: el.getAttribute("href"), x: Math.min(vw - 3, r.right - 3), y: r.top + r.height / 2 };
    });
    if (isPhoneProject(info.project.name)) await page.touchscreen.tap(hedef.x, hedef.y);
    else await page.mouse.click(hedef.x, hedef.y);
    await expect(page).toHaveURL(new RegExp(hedef.href.replace(".", "\\.") + "$"));
  });

  test("klavye: geri yönde (Shift+Tab) odaklanan bağlantı sol solma bölgesinin altında kalmaz", async ({ page, browserName }, info) => {
    test.skip(isPhoneProject(info.project.name), "not_applicable: klavye denetimi masaüstü motorlarında yapılır");
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("hakkinda.html");
    const links = page.locator("#site-nav-list a");
    await links.last().focus();
    const geri = browserName === "webkit" ? "Alt+Shift+Tab" : "Shift+Tab";
    for (let i = 0; i < 4; i++) await page.keyboard.press(geri);
    const r = await page.evaluate(() => {
      const el = document.activeElement, list = document.getElementById("site-nav-list");
      // Eşik solma genişliği tokenından okunur (şeridin sağ iç boşluğu bu tokendır), kaydırma dolgusundan değil.
      const fade = parseFloat(getComputedStyle(list).paddingRight);
      return { ad: el.textContent, sol: el.getBoundingClientRect().left, sinir: list.getBoundingClientRect().left + fade, fade, kay: list.scrollLeft, icinde: !!el.closest("#site-nav-list") };
    });
    expect(r.icinde, `odak şeritte (${r.ad})`).toBe(true);
    expect(r.fade, "solma genişliği 40 CSS px").toBe(40);
    expect(r.kay, "şerit hâlâ kaydırılmış durumda (sol kenar soluyor)").toBeGreaterThan(0);
    expect(r.sol, `${r.ad}: sol kenar solma bölgesinin sağında`).toBeGreaterThanOrEqual(r.sinir - 1);
  });

  test("alt gezinme şeritle aynı sayfaları aynı adlarla verir", async ({ page }) => {
    await page.goto("index.html");
    const oku = (sel) => page.locator(sel).evaluateAll((els) => els.map((a) => a.textContent.trim() + " > " + a.getAttribute("href")));
    expect(await oku(".footer-nav a")).toEqual(await oku("#site-nav-list a"));
  });
});

test.describe("içerik tutarlılığı", () => {
  test("özet: kısa liste başlığı altındaki satır sayısı huninin kısa liste sayısına eşit", async ({ page }) => {
    await page.goto("index.html");
    const huni = parseInt(await page.locator(".funnel__row--key .funnel__num").first().textContent(), 10);
    await expect(page.locator("#kisa-liste-satirlar > li")).toHaveCount(huni);
    const kararlar = await page.locator("#kisa-liste-satirlar > li .tag").evaluateAll((els) => [...new Set(els.map((x) => x.dataset.karar))]);
    expect(kararlar.every((k) => ["once-test-et", "yatirim-yap"].includes(k)), `kısa listedeki kararlar: ${kararlar.join(", ")}`).toBe(true);
    await expect(page.locator(".opts__more")).toHaveText("Kısa listenin hemen dışında");
  });

  test("sıralama: hedef tutarı işaretler bölümünde herkes için yazılı", async ({ page }) => {
    await page.goto("siralama.html");
    const d = page.locator("details.howto");
    await d.locator("summary").click();
    await expect(d).toContainText("USD");
    await expect(d).toContainText("ölçek dışına taşıyor");
  });
});

test.describe("bölüm gezintisi: bulunulan bölüm", () => {
  test("sayfa kaydıkça ilgili bağlantı işaretlenir, sayfa başında hiçbiri işaretli değildir", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("proje/qral.html");
    await expect(page.locator(".toc__list a[aria-current]")).toHaveCount(0);
    await page.locator("#bugun").evaluate((el) => el.scrollIntoView());
    const cur = page.locator(".toc__list a[aria-current]");
    await expect(cur).toHaveCount(1);
    await expect(cur).toHaveText("Bugün");
    await expect(cur).toHaveAttribute("aria-current", "location");
    const r = await cur.evaluate((el) => { const b = el.getBoundingClientRect(); return { sol: b.left, sag: b.right, vw: document.documentElement.clientWidth }; });
    expect(r.sol).toBeGreaterThanOrEqual(0);
    expect(r.sag, "işaretli bağlantı şeritte görünür").toBeLessThanOrEqual(r.vw);
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    await expect(page.locator(".toc__list a[aria-current]")).toHaveText(await page.locator(".toc__list a").last().textContent());
    await page.evaluate(() => window.scrollTo(0, 0));
    await expect(page.locator(".toc__list a[aria-current]")).toHaveCount(0);
  });

  test("gezinti bağlantısına basınca o bölüm işaretlenir (yüzde 200 yazıda da)", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("proje/qral.html");
    for (const buyut of [false, true]) {
      if (buyut) await page.evaluate(() => { document.documentElement.style.fontSize = "200%"; });
      await page.locator(".toc__list a", { hasText: "İki çalışma" }).click();
      await expect(page.locator(".toc__list a[aria-current]"), buyut ? "yüzde 200 yazı" : "olağan yazı").toHaveText("İki çalışma");
      await page.evaluate(() => window.scrollTo(0, 0));
    }
  });
});

test.describe("telefon tabloları", () => {
  test("390 genişlikte kanıt ölçeği kaymadan sığar; kod sütunu dar, açıklama geniş", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("sablon.html");
    const m = await page.locator("#kanit .table-wrap").evaluate((w) => {
      const th = w.querySelector("tbody th").getBoundingClientRect(), td = w.querySelector("tbody td").getBoundingClientRect();
      return { sw: w.scrollWidth, cw: w.clientWidth, kod: th.width, anlam: td.width, kenar: w.getAttribute("data-kenar") };
    });
    expect(m.sw, "tablo kendi alanına sığıyor").toBeLessThanOrEqual(m.cw);
    expect(m.kod, "kod sütunu dar").toBeLessThan(64);
    expect(m.anlam, "açıklama sütunu geniş").toBeGreaterThan(180);
    expect(m.kenar, "taşmayan tabloda kenar durumu yazılmaz").toBeNull();
  });

  test("390 genişlikte taşan tabloda ilk sütun yerinde kalır ve devamı olan kenar belirtilir", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("duyarlilik.html");
    const wrap = page.locator("#sira .table-wrap");
    await expect(wrap).toHaveAttribute("data-kenar", "bas");
    expect(await wrap.evaluate((el) => getComputedStyle(el).maskImage), "sağ kenar soluyor").toContain("gradient");
    const once = await wrap.evaluate((w) => w.querySelector("tbody th").getBoundingClientRect().left);
    const tasma = await wrap.evaluate((w) => w.scrollWidth - w.clientWidth);
    expect(tasma, "tablo 390 genişlikte taşıyor").toBeGreaterThan(20);
    await wrap.evaluate((w) => { w.scrollLeft = Math.round((w.scrollWidth - w.clientWidth) / 2); });
    await expect(wrap).toHaveAttribute("data-kenar", "orta");
    const sonra = await wrap.evaluate((w) => ({ th: w.querySelector("tbody th").getBoundingClientRect().left, td: w.querySelector("tbody td").getBoundingClientRect().left, w: w.getBoundingClientRect().left }));
    expect(Math.abs(sonra.th - once), "satır adı yatay kaydırmada yerinde kalır").toBeLessThan(1);
    expect(sonra.td, "sayı sütunları satır adının altından kayar").toBeLessThan(sonra.th + 100);
    await wrap.evaluate((w) => { w.scrollLeft = w.scrollWidth; });
    await expect(wrap).toHaveAttribute("data-kenar", "son");
    expect(await wrap.evaluate((el) => getComputedStyle(el).maskImage), "sonda kenar solmaz").toBe("none");
  });

  test("390 genişlikte belirleyici sütunlar kaydırmadan görünür ve sütun başlıklarının altında boş bant kalmaz", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    for (const [url, sel, basliklar] of [["duyarlilik.html", "#sira", ["Sıra aralığı", "İlk 10'da"]], ["duyarlilik.html", "#setler", ["Uyum"]], ["portfoy.html", "#taban", ["Saat başı", "Karar"]], ["portfoy.html", "#saat", ["Saat başı"]]]) {
      await page.goto(url);
      const m = await page.locator(`${sel} .table-wrap`).evaluate((w, adlar) => {
        const kutu = w.getBoundingClientRect(), fade = w.hasAttribute("data-kenar") ? 40 : 0;
        const ths = [...w.querySelectorAll("thead th")];
        const gorunen = adlar.map((ad) => { const th = ths.find((x) => x.textContent.trim() === ad); return th ? th.getBoundingClientRect().right <= kutu.right - fade + 1 : null; });
        // Başlık satırı: en uzun başlığın yüksekliği ile en kısa başlığın altındaki boşluk
        const satir = w.querySelector("thead tr").getBoundingClientRect();
        const bosluk = Math.max(...ths.map((th) => { const r = document.createRange(); r.selectNodeContents(th); const b = r.getBoundingClientRect(); return b.height ? satir.bottom - b.bottom : 0; }));
        return { gorunen, bosluk: Math.round(bosluk) };
      }, basliklar);
      expect(m.gorunen, `${url} ${sel}: ${basliklar.join(", ")} kaydırmadan görünür`).toEqual(basliklar.map(() => true));
      expect(m.bosluk, `${url} ${sel}: başlık metninin altındaki boşluk`).toBeLessThanOrEqual(12);
    }
  });

  test("taşan tablo klavyeyle odaklanınca maske kalkar ve çerçevesi kırpılmaz", async ({ page, browserName }, info) => {
    test.skip(isPhoneProject(info.project.name), "not_applicable: klavye denetimi masaüstü motorlarında yapılır");
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("duyarlilik.html");
    const wrap = page.locator("#sira .table-wrap");
    await expect(wrap).toHaveAttribute("data-kenar", "bas");
    await page.locator("#setler .table-wrap").focus();
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press(browserName === "webkit" ? "Alt+Tab" : "Tab");
      if (await wrap.evaluate((el) => el === document.activeElement)) break;
    }
    await expect(wrap).toBeFocused();
    const s = await wrap.evaluate((el) => { const cs = getComputedStyle(el); return { mask: cs.maskImage, stil: cs.outlineStyle, genislik: parseFloat(cs.outlineWidth), ofset: parseFloat(cs.outlineOffset), sol: el.getBoundingClientRect().left, sag: el.getBoundingClientRect().right, vw: document.documentElement.clientWidth }; });
    expect(s.mask, "odakta maske yok").toBe("none");
    expect(s.stil).toBe("solid");
    expect(s.sol - s.ofset - s.genislik, "çerçevenin sol kenarı ekranın içinde").toBeGreaterThanOrEqual(0);
    expect(s.sag + s.ofset + s.genislik, "çerçevenin sağ kenarı ekranın içinde").toBeLessThanOrEqual(s.vw);
    // İlk sütundaki bağlantının çerçevesi bölge kutusunun içinde kalır.
    const link = wrap.locator("tbody th a").first();
    await link.focus();
    const k = await link.evaluate((el) => { const cs = getComputedStyle(el), r = el.getBoundingClientRect(), w = el.closest(".table-wrap").getBoundingClientRect(); return { sol: r.left - parseFloat(cs.outlineOffset) - parseFloat(cs.outlineWidth), kutu: w.left }; });
    expect(k.sol, "bağlantı çerçevesinin sol kenarı bölge kutusunun içinde").toBeGreaterThanOrEqual(k.kutu - 0.5);
  });

  test("portföy karşılaştırma tablosunda boş satır yüksekliği yok", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("portfoy.html");
    const fazla = await page.locator("#taban tbody tr").evaluateAll((rows) => rows.map((tr) => {
      const icerik = Math.max(...[...tr.children].map((c) => { const r = document.createRange(); r.selectNodeContents(c); return r.getBoundingClientRect().height; }));
      return Math.round(tr.getBoundingClientRect().height - icerik);
    }));
    expect(Math.max(...fazla), `satır yüksekliği ile en uzun hücre içeriği arasındaki fark: ${fazla.join(", ")}`).toBeLessThanOrEqual(24);
  });
});

test.describe("betik yüklenemezse", () => {
  test("arama ve süzgeç görünmez ama yeri ayrılır; betikle görünür olur ve yerleşim aynı kalır", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("siralama.html");
    await expect(page.locator("#suzgec")).toBeVisible();
    const betikli = await page.locator("#liste").evaluate((el) => el.getBoundingClientRect().top);
    await page.route("**/assets/site.js", (r) => r.abort());
    await page.goto("siralama.html");
    await expect(page.locator("#suzgec")).toBeHidden();
    expect(await page.evaluate(() => document.documentElement.classList.contains("js"))).toBe(false);
    const betiksiz = await page.locator("#liste").evaluate((el) => el.getBoundingClientRect().top);
    expect(Math.abs(betikli - betiksiz), "liste aynı yerde başlar (yerleşim kaymaz)").toBeLessThanOrEqual(1);
    await expect(page.locator("#liste > li").first().locator(".opt__title a")).toBeVisible();
  });
});

test("zorunlu renk kipi: kapak hunisinde dolgu izden ayrışır", async ({ page }, info) => {
  test.skip(info.project.name !== "chromium", "not_run: zorunlu renk emülasyonu yalnız Chromium'da var");
  await page.emulateMedia({ forcedColors: "active" });
  await page.goto("index.html");
  const r = await page.locator(".cover .funnel__row").evaluateAll((rows) => rows.map((row) => ({
    iz: getComputedStyle(row.querySelector(".funnel__bar")).backgroundColor, dolgu: getComputedStyle(row.querySelector(".funnel__fill")).backgroundColor,
  })));
  expect(r.length).toBeGreaterThan(3);
  expect(r.filter((x) => x.iz === x.dolgu), "izle aynı renkte dolgu").toEqual([]);
});
