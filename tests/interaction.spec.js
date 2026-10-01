// Etkileşim: menü, atlama bağlantıları, görünür klavye odağı, süzme ve sıralama, sözlük, bölüm gezintisi, yön değişimi, betiksiz temel deneyim.
import { test, expect } from "@playwright/test";
import { KEY_PAGES, isPhoneProject, tabKey, shiftTabKey } from "./helpers.js";

async function focusInfo(page) {
  return page.evaluate(() => {
    const el = document.activeElement;
    if (!el || el === document.body) return null;
    const cs = getComputedStyle(el);
    const probe = document.createElement("span");
    probe.style.color = getComputedStyle(document.documentElement).getPropertyValue("--c-focus").trim();
    document.body.appendChild(probe);
    const ringRgb = getComputedStyle(probe).color;
    probe.remove();
    const parents = [];
    for (let p = el.parentElement; p; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (s.outlineStyle !== "none" && parseFloat(s.outlineWidth) > 0) parents.push(p.tagName.toLowerCase() + "." + p.className);
    }
    const r = el.getBoundingClientRect();
    if (!el.dataset.qaId) el.dataset.qaId = String(Math.random());
    return {
      id: el.dataset.qaId, etiket: el.tagName.toLowerCase() + "." + el.className, metin: el.textContent.trim().slice(0, 40),
      outlineStyle: cs.outlineStyle, outlineWidth: parseFloat(cs.outlineWidth), outlineColor: cs.outlineColor, ringRgb,
      boxShadow: cs.boxShadow, cerceveliUst: parents, gorunur: r.width > 0 && r.height > 0,
    };
  });
}

/** Odak ilk durağa dönene ya da sınır dolana kadar Tab ile dolaşır; her durakta odak göstergesini denetler. */
async function focusCycle(page, browserName, label, limit = 450) {
  const seen = new Set(); let first = null; let n = 0;
  for (let i = 0; i < limit; i++) {
    await page.keyboard.press(tabKey(browserName));
    const f = await focusInfo(page);
    if (!f) continue;
    if (first === null) first = f.id;
    else if (f.id === first) break;
    if (seen.has(f.id)) continue;
    seen.add(f.id); n++;
    expect.soft(f.outlineStyle, `${label} durak ${i} ${f.etiket}: çerçeve türü`).toBe("solid");
    expect.soft(f.outlineWidth, `${label} durak ${i} ${f.etiket}: çerçeve kalınlığı`).toBeGreaterThanOrEqual(3);
    expect.soft(f.outlineColor, `${label} durak ${i} ${f.etiket}: çerçeve rengi token`).toBe(f.ringRgb);
    expect.soft(f.boxShadow, `${label} durak ${i} ${f.etiket}: ek gölge çerçevesi yok`).toBe("none");
    expect.soft(f.cerceveliUst, `${label} durak ${i} ${f.etiket}: üst kapsayıcıda çerçeve yok`).toEqual([]);
    expect.soft(f.gorunur, `${label} durak ${i} ${f.etiket}: odaklanan öğe görünür`).toBe(true);
  }
  return n;
}

test.describe("menü (dar ekran)", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("index.html");
  });

  test("ilk çizimde menü kapalı; düğme açar, kapatır ve durumunu bildirir", async ({ page }) => {
    const toggle = page.locator(".nav-toggle");
    const list = page.locator("#site-nav-list");
    await expect(toggle).toBeVisible();
    await expect(toggle).toHaveJSProperty("tagName", "BUTTON");
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await expect(list).toBeHidden();
    await toggle.click();
    await expect(toggle).toHaveAttribute("aria-expanded", "true");
    await expect(list).toBeVisible();
    await expect(list.locator("a")).toHaveCount(9);
    await toggle.click();
    await expect(list).toBeHidden();
  });

  test("klavye: Enter açar, Escape menü içindeyken kapatır ve odağı düğmeye döndürür", async ({ page, browserName }, info) => {
    test.skip(isPhoneProject(info.project.name), "not_applicable: klavye denetimi masaüstü motorlarında yapılır");
    const toggle = page.locator(".nav-toggle");
    await toggle.focus();
    await page.keyboard.press("Enter");
    await expect(toggle).toHaveAttribute("aria-expanded", "true");
    await page.keyboard.press(tabKey(browserName));
    await expect(page.locator("#site-nav-list a").first()).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await expect(toggle).toBeFocused();
    await expect(page.locator("#site-nav-list")).toBeHidden();
  });

  test("Escape menü dışındayken odağı kaçırmaz", async ({ page }) => {
    await page.goto("siralama.html");
    await page.locator(".nav-toggle").click();
    const q = page.locator("#q");
    await q.focus();
    await page.keyboard.press("Escape");
    await expect(q).toBeFocused();
  });

  test("geçerli sayfa menüde işaretli", async ({ page }) => {
    await page.locator(".nav-toggle").click();
    await expect(page.locator('#site-nav-list a[aria-current="page"]')).toHaveText("Özet");
    await page.locator("#site-nav-list a", { hasText: "Sıralama" }).click();
    await expect(page).toHaveURL(/siralama\.html/);
    await page.locator(".nav-toggle").click();
    await expect(page.locator('#site-nav-list a[aria-current="page"]')).toHaveText("Sıralama");
  });

  test("menü düğmesinin klavye odağı görünür", async ({ page, browserName }, info) => {
    test.skip(isPhoneProject(info.project.name), "not_applicable: klavye denetimi masaüstü motorlarında yapılır");
    await page.keyboard.press(tabKey(browserName));
    await page.keyboard.press(tabKey(browserName));
    await page.keyboard.press(tabKey(browserName));
    const f = await focusInfo(page);
    expect(f.etiket).toContain("nav-toggle");
    expect(f.outlineStyle).toBe("solid");
  });
});

test("geniş ekranda menü hep açık, düğme gizli", async ({ page }, info) => {
  test.skip(isPhoneProject(info.project.name), "not_applicable: geniş ekran denetimi masaüstü motorlarında yapılır");
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("index.html");
  await expect(page.locator(".nav-toggle")).toBeHidden();
  await expect(page.locator("#site-nav-list")).toBeVisible();
});

test.describe("klavye ve odak", () => {
  test.beforeEach(async ({}, info) => {
    test.skip(isPhoneProject(info.project.name), "not_applicable: klavye denetimi masaüstü motorlarında yapılır");
  });

  test("atlama bağlantısı ilk durak; sonraki durak ana içerikte", async ({ page, browserName }) => {
    await page.goto("siralama.html");
    await page.keyboard.press(tabKey(browserName));
    const skip = page.locator(".skip-link");
    await expect(skip).toBeFocused();
    await expect(skip).toBeInViewport();
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(/#icerik$/);
    await page.keyboard.press(tabKey(browserName));
    expect(await page.evaluate(() => !!document.activeElement && !!document.activeElement.closest("main"))).toBe(true);
  });

  test("sıralamada süzgeçlerden sonra listeye geç bağlantısı odakla görünür ve listeye götürür", async ({ page, browserName }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("siralama.html");
    const link = page.locator(".skip-inline a");
    await link.focus();
    await expect(link).toBeInViewport();
    const w = await link.evaluate((el) => el.getBoundingClientRect().width);
    expect(w).toBeGreaterThan(20);
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(/#liste-baslik$/);
    await page.keyboard.press(tabKey(browserName));
    expect(await page.evaluate(() => !!document.activeElement.closest("#liste"))).toBe(true);
  });

  for (const url of KEY_PAGES) {
    test(`odak göstergesi: ${url} üzerinde bütün duraklarda tek ve görünür`, async ({ page, browserName }) => {
      test.setTimeout(180_000);
      await page.setViewportSize({ width: 1280, height: 800 });
      await page.goto(url);
      const n = await focusCycle(page, browserName, url);
      expect(n, `${url}: klavye durağı sayısı`).toBeGreaterThan(5);
    });
  }

  test("odak göstergesi: 320 genişlikte menü açıkken bütün duraklarda görünür", async ({ page, browserName }) => {
    test.setTimeout(180_000);
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("index.html");
    await page.locator(".nav-toggle").click();
    const n = await focusCycle(page, browserName, "320 menü açık");
    expect(n).toBeGreaterThan(15);
  });

  test("Shift+Tab geri gider", async ({ page, browserName }) => {
    await page.goto("index.html");
    const key = tabKey(browserName);
    await page.keyboard.press(key);
    await page.keyboard.press(key);
    await page.keyboard.press(key);
    const third = await focusInfo(page);
    await page.keyboard.press(key);
    await page.keyboard.press(shiftTabKey(browserName));
    const back = await focusInfo(page);
    expect(back.id).toBe(third.id);
  });

  test("açılır bölüm klavyeyle açılır ve kapanır", async ({ page }) => {
    await page.goto("sablon.html");
    const first = page.locator("#kapilar details").first();
    await first.locator("summary").focus();
    await expect(first).not.toHaveAttribute("open", "");
    await page.keyboard.press("Enter");
    await expect(first).toHaveAttribute("open", "");
    await expect(first.locator(".details__body")).toBeVisible();
    await page.keyboard.press("Space");
    await expect(first).not.toHaveAttribute("open", "");
  });

  test("fare tıklaması odak çerçevesi bırakmıyor, klavye bırakıyor", async ({ page, browserName }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("siralama.html");
    const chip = page.locator('.chip[data-sort="puan"]');
    await chip.click();
    expect(await chip.evaluate((el) => getComputedStyle(el).outlineStyle)).toBe("none");
    await page.keyboard.press(tabKey(browserName));
    expect((await focusInfo(page)).outlineStyle).toBe("solid");
  });
});

test.describe("sıralama sayfası: süzme, arama, sıralama", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("siralama.html");
  });

  const visibleRows = (page) => page.locator("#liste > li:not([hidden])");
  async function openPanel(page) {
    const panel = page.locator("#suzgec-panel");
    if (!(await panel.evaluate((el) => el.open))) await panel.locator("summary").click();
  }

  test("karar süzgeci listeyi daraltır, sayaç ve düğme durumu güncellenir", async ({ page }) => {
    await openPanel(page);
    const total = await page.locator("#liste > li").count();
    await expect(page.locator("#sonuc")).toHaveText(`${total} seçenek gösteriliyor`);
    const chip = page.locator('.chip[data-filter="karar"]:not([data-value=""])').first();
    const value = await chip.getAttribute("data-value");
    await chip.click();
    await expect(chip).toHaveAttribute("aria-pressed", "true");
    await expect(page.locator('.chip[data-filter="karar"][data-value=""]')).toHaveAttribute("aria-pressed", "false");
    const n = await visibleRows(page).count();
    expect(n).toBeGreaterThan(0);
    expect(n).toBeLessThan(total);
    await expect(page.locator("#sonuc")).toHaveText(`${n} seçenek gösteriliyor`);
    expect(await visibleRows(page).evaluateAll((els) => [...new Set(els.map((x) => x.dataset.karar))])).toEqual([value]);
  });

  test("nakit süzgeci karar süzgeciyle birlikte çalışır ve özet satırı güncellenir", async ({ page }) => {
    await openPanel(page);
    const chip = page.locator('.chip[data-filter="nsinif"]:not([data-value=""])').last();
    const value = await chip.getAttribute("data-value");
    await chip.click();
    expect(await visibleRows(page).evaluateAll((els) => [...new Set(els.map((x) => x.dataset.nsinif))])).toEqual([value]);
    await expect(page.locator("#suzgec-ozet")).toContainText((await chip.textContent()).toLocaleLowerCase("tr"));
    await page.locator('.chip[data-filter="karar"][data-value="degistir"]').click();
    expect(await visibleRows(page).evaluateAll((els) => [...new Set(els.map((x) => x.dataset.karar + "|" + x.dataset.nsinif))])).toEqual([`degistir|${value}`]);
    await page.locator('.chip[data-filter="nsinif"][data-value=""]').click();
    await page.locator('.chip[data-filter="karar"][data-value=""]').click();
    await expect(page.locator("#suzgec-ozet")).toHaveText("tümü · yatırım sırası");
  });

  test("bütün sıralama düğmeleri listeyi doğru yönde dizer", async ({ page }) => {
    await openPanel(page);
    const yon = { yatirim: 1, puan: -1, nakit: -1, sure: 1, ogrenme: 1, stratejik: -1 };
    for (const [key, d] of Object.entries(yon)) {
      await page.locator(`.chip[data-sort="${key}"]`).click();
      const vals = await visibleRows(page).evaluateAll((els, k) => els.map((x) => parseFloat(x.dataset[k])), key);
      expect(vals, `sıralama: ${key}`).toEqual([...vals].sort((a, b) => d * (a - b)));
    }
  });

  test("arama Türkçe harflere duyarsız", async ({ page }) => {
    const q = page.locator("#q");
    const counts = [];
    for (const term of ["danışmanlık", "DANIŞMANLIK", "danismanlik", "Danişmanlik"]) {
      await q.fill(term);
      await expect.poll(async () => page.locator("#liste > li:not([hidden])").count()).toBeGreaterThan(0);
      counts.push(await visibleRows(page).count());
    }
    expect(new Set(counts).size, `sonuç sayıları: ${counts.join(", ")}`).toBe(1);
  });

  test("eşleşme yoksa boş durum görünür ve süzgeçler temizlenebilir", async ({ page }) => {
    const total = await page.locator("#liste > li").count();
    await page.locator("#q").fill("zzzzqqqq-yok");
    await expect(page.locator("#sonuc")).toHaveText("0 seçenek gösteriliyor");
    await expect(page.locator("#bos")).toBeVisible();
    await page.locator("#temizle").click();
    await expect(page.locator("#bos")).toBeHidden();
    await expect(visibleRows(page)).toHaveCount(total);
    await expect(page.locator("#q")).toBeFocused();
  });

  test("klavye: düğme Enter ve boşlukla çalışır", async ({ page }, info) => {
    test.skip(isPhoneProject(info.project.name), "not_applicable: klavye denetimi masaüstü motorlarında yapılır");
    await openPanel(page);
    const chip = page.locator('.chip[data-sort="puan"]');
    await chip.focus();
    await page.keyboard.press("Enter");
    await expect(chip).toHaveAttribute("aria-pressed", "true");
    const other = page.locator('.chip[data-sort="ogrenme"]');
    await other.focus();
    await page.keyboard.press("Space");
    await expect(other).toHaveAttribute("aria-pressed", "true");
    await expect(chip).toHaveAttribute("aria-pressed", "false");
  });

  test("seçim adreste saklanır ve yenilenince korunur; arama metni adrese yazılmaz", async ({ page }) => {
    await openPanel(page);
    const chip = page.locator('.chip[data-filter="karar"]:not([data-value=""])').first();
    const value = await chip.getAttribute("data-value");
    await chip.click();
    await page.locator('.chip[data-sort="puan"]').click();
    await page.locator("#q").fill("hizmet");
    await expect(page).toHaveURL(new RegExp(`karar=${value}`));
    await expect(page).toHaveURL(/sirala=puan/);
    expect(page.url()).not.toContain("hizmet");
    await page.reload();
    await expect(page.locator(`.chip[data-filter="karar"][data-value="${value}"]`)).toHaveAttribute("aria-pressed", "true");
    await expect(page.locator('.chip[data-sort="puan"]')).toHaveAttribute("aria-pressed", "true");
  });

  test("yön değişimi: yazılan arama, açık panel ve odak korunur", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("siralama.html");
    await openPanel(page);
    const q = page.locator("#q");
    await q.fill("hizmet");
    await expect.poll(() => visibleRows(page).count()).toBeLessThan(132);
    const n = await visibleRows(page).count();
    await page.setViewportSize({ width: 844, height: 390 });
    await expect(q).toHaveValue("hizmet");
    await expect(q).toBeFocused();
    expect(await page.locator("#suzgec-panel").evaluate((el) => el.open)).toBe(true);
    await expect(visibleRows(page)).toHaveCount(n);
  });

  test("seçenek başlığı proje sayfasındaki ilgili bölüme götürür ve başlık gezinti altında kalmaz", async ({ page }) => {
    const link = visibleRows(page).first().locator(".opt__title a");
    const href = await link.getAttribute("href");
    await link.click();
    const id = href.split("#")[1];
    const target = page.locator(`[id="${id}"] h2`);
    await expect(target).toBeInViewport();
    const tocBottom = await page.locator(".toc").evaluate((el) => el.getBoundingClientRect().bottom);
    const top = await target.evaluate((el) => el.getBoundingClientRect().top);
    expect(top).toBeGreaterThanOrEqual(tocBottom - 1);
  });
});

test.describe("proje sözlüğü", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("projeler.html");
  });
  const visible = (page) => page.locator("#sozluk-liste .glossary > li:not([hidden])");

  test("her proje için ad, tür ve tek cümlelik yanıt var", async ({ page }) => {
    const items = page.locator("#sozluk-liste .glossary > li");
    await expect(items).toHaveCount(45);
    const eksik = await items.evaluateAll((els) => els.filter((li) => !li.querySelector(".glossary__name")?.textContent.trim() || !li.querySelector(".glossary__type")?.textContent.trim() || (li.querySelector(".glossary__desc")?.textContent.trim().length || 0) < 40).length);
    expect(eksik).toBe(0);
  });

  test("arama Türkçe harflere duyarsız ve boş harf grupları gizlenir", async ({ page }) => {
    const sq = page.locator("#sq");
    await sq.fill("QR");
    await expect.poll(() => visible(page).count()).toBeGreaterThan(0);
    const n1 = await visible(page).count();
    await sq.fill("qr");
    await expect(visible(page)).toHaveCount(n1);
    const bosGrup = await page.locator("#sozluk-liste .glossary__group").evaluateAll((gs) => gs.filter((g) => !g.hidden && !g.querySelector(".glossary > li:not([hidden])")).length);
    expect(bosGrup).toBe(0);
    await sq.fill("ŞÇĞÜÖİ-yok");
    await expect(page.locator("#sozluk-bos")).toBeVisible();
    await expect(page.locator("#sozluk-sonuc")).toHaveText("0 proje");
  });

  test("tür süzgeci listeyi daraltır ve sayaç güncellenir", async ({ page }) => {
    const panel = page.locator("#sozluk-panel");
    if (!(await panel.evaluate((el) => el.open))) await panel.locator("summary").click();
    const chip = page.locator('.chip[data-gfilter="Hizmet"]');
    await chip.click();
    await expect(chip).toHaveAttribute("aria-pressed", "true");
    const grups = await visible(page).evaluateAll((els) => [...new Set(els.map((x) => x.dataset.grup))]);
    expect(grups).toEqual(["Hizmet"]);
    const n = await visible(page).count();
    await expect(page.locator("#sozluk-sonuc")).toHaveText(`${n} proje`);
  });

  test("ada dokununca proje sayfası \"bu nedir\" yanıtıyla açılır", async ({ page }) => {
    await page.locator(".glossary__link", { hasText: "qral" }).click();
    await expect(page).toHaveURL(/proje\/qral\.html$/);
    await expect(page.locator(".answer")).toContainText("Chrome uzantısı");
    await expect(page.locator("#nedir .steps > li")).not.toHaveCount(0);
  });
});

test.describe("dokunma", () => {
  test("dokunarak menü ve süzme çalışır", async ({ page }, info) => {
    test.skip(!isPhoneProject(info.project.name), "not_applicable: yalnız dokunmatik telefon profilleri");
    await page.goto("siralama.html");
    await page.locator(".nav-toggle").tap();
    await expect(page.locator("#site-nav-list")).toBeVisible();
    await page.locator(".nav-toggle").tap();
    await page.locator("#suzgec-panel > summary").tap();
    const chip = page.locator('.chip[data-filter="karar"]:not([data-value=""])').first();
    await chip.tap();
    await expect(chip).toHaveAttribute("aria-pressed", "true");
  });

  test("bölüm gezintisi dokunarak çalışır", async ({ page }, info) => {
    test.skip(!isPhoneProject(info.project.name), "not_applicable: yalnız dokunmatik telefon profilleri");
    await page.goto("proje/qral.html");
    await page.locator(".toc__list a", { hasText: "Bugün" }).tap();
    await expect(page).toHaveURL(/#bugun$/);
    await expect(page.locator("#bugun h2")).toBeInViewport();
  });
});

test("hover yalnız biçim değiştirir; içerik gizleyip gösteren hover kuralı yok", async ({}, info) => {
  test.skip(info.project.name !== "chromium", "not_applicable: dosya düzeyi denetim tek projede yeterli");
  const fs = await import("node:fs");
  const path = await import("node:path");
  const { ROOT } = await import("./helpers.js");
  const css = ["base.css", "components.css"].map((f) => fs.readFileSync(path.join(ROOT, "src", "styles", f), "utf8")).join("\n");
  const bad = [...css.matchAll(/([^{}]*:hover[^{}]*)\{([^}]*)\}/g)].filter((m) => /\b(display|visibility|opacity|clip|clip-path|max-height)\s*:/.test(m[2])).map((m) => m[1].trim());
  expect(bad).toEqual([]);
});

test.describe("betiksiz temel deneyim", () => {
  test.use({ javaScriptEnabled: false });

  test("betik kapalıyken menü bağlantısı listeyi açar ve gezinme çalışır", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("siralama.html");
    const link = page.locator("a.nav-toggle");
    await expect(link).toBeVisible();
    await expect(page.locator("#site-nav-list")).toBeHidden();
    await link.click();
    await expect(page.locator("#site-nav-list")).toBeVisible();
    await page.locator("#site-nav-list a", { hasText: "Projeler" }).click();
    await expect(page).toHaveURL(/projeler\.html/);
    await expect(page.locator("#sozluk-liste .glossary > li")).toHaveCount(45);
    await expect(page.locator("#sozluk-arac")).toBeHidden();
  });

  test("betik kapalıyken liste, açılır bölümler ve kaydırma bölgeleri çalışır", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("siralama.html");
    await expect(page.locator("#suzgec")).toBeHidden();
    const rows = page.locator("#liste > li");
    expect(await rows.count()).toBeGreaterThan(50);
    await rows.first().locator(".opt__title a").click();
    await expect(page.locator("h1")).toBeVisible();
    await page.goto("sablon.html");
    const first = page.locator("#kapilar details").first();
    await first.locator("summary").click();
    await expect(first.locator(".details__body")).toBeVisible();
    await page.goto("duyarlilik.html");
    await expect(page.locator(".table-wrap").first()).toHaveAttribute("tabindex", "0");
  });
});
