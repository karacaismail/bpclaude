// Görsel regresyon: sabit ortamda (aynı makine, aynı motor sürümü) piksel toleransı olmadan karşılaştırma.
// Referanslar tests/__snapshots__/<platform>/<proje>/ altındadır; değişiklik önce, sonra ve gerekçesiyle qa/referans-degisiklikleri altına yazılır.
import { test, expect } from "@playwright/test";
import { SAMPLE_PROJECTS, isPhoneProject, tabKey } from "./helpers.js";

const SIZES = [{ ad: "320", width: 320, height: 568 }, { ad: "390", width: 390, height: 844 }, { ad: "1280", width: 1280, height: 800 }];
const settle = (page) => page.evaluate(() => document.fonts.ready);
const telefonGenis = (info, w) => isPhoneProject(info.project.name) && w > 400;

for (const size of SIZES) {
  test(`görsel: özet ${size.ad}`, async ({ page }, info) => {
    test.skip(telefonGenis(info, size.width), "not_applicable: telefon profili yalnız telefon genişliklerinde");
    await page.setViewportSize({ width: size.width, height: size.height });
    await page.goto("index.html");
    await settle(page);
    await expect(page).toHaveScreenshot(`ozet-${size.ad}.png`);
  });

  test(`görsel: sıralama ${size.ad}`, async ({ page }, info) => {
    test.skip(telefonGenis(info, size.width), "not_applicable: telefon profili yalnız telefon genişliklerinde");
    await page.setViewportSize({ width: size.width, height: size.height });
    await page.goto("siralama.html");
    await settle(page);
    await expect(page).toHaveScreenshot(`siralama-${size.ad}.png`);
    await page.setViewportSize({ width: size.width, height: 2400 });
    await expect(page.locator("#liste > li").first()).toHaveScreenshot(`secenek-satiri-${size.ad}.png`);
  });

  test(`görsel: proje sayfası ${size.ad}`, async ({ page }, info) => {
    test.skip(telefonGenis(info, size.width), "not_applicable: telefon profili yalnız telefon genişliklerinde");
    await page.setViewportSize({ width: size.width, height: size.height });
    await page.goto(SAMPLE_PROJECTS[1]);
    await settle(page);
    await expect(page).toHaveScreenshot(`proje-${size.ad}.png`);
    // Öğe görüntüleri uzatılmış görünüm alanında alınır (genişlik aynı): görünüm alanına sığmayan öğe kırpılmasın.
    await page.setViewportSize({ width: size.width, height: 2400 });
    await expect(page.locator("#nedir")).toHaveScreenshot(`nedir-${size.ad}.png`);
    const first = page.locator("main section.section[id$='-a']");
    await first.locator("details").first().evaluate((el) => { el.open = true; });
    await expect(first.locator(".gates")).toHaveScreenshot(`kapilar-${size.ad}.png`);
    await expect(first.locator(".crits").first()).toHaveScreenshot(`kriterler-${size.ad}.png`);
  });

  test(`görsel: proje sözlüğü ${size.ad}`, async ({ page }, info) => {
    test.skip(telefonGenis(info, size.width), "not_applicable: telefon profili yalnız telefon genişliklerinde");
    await page.setViewportSize({ width: size.width, height: 2400 });
    await page.goto("projeler.html");
    await settle(page);
    await expect(page.locator("#sozluk-liste .glossary__group").first()).toHaveScreenshot(`sozluk-a-${size.ad}.png`);
  });
}

test("görsel: gezinme şeridi 320 ve karar dağılımı", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.goto("siralama.html");
  await settle(page);
  await expect(page.locator(".site-header")).toHaveScreenshot("gezinme-seridi-320.png");
  await expect(page.locator(".dist")).toHaveScreenshot("karar-dagilimi-320.png");
});

test("görsel: yatay telefon 844×390 ve tablet 768", async ({ page }, info) => {
  test.skip(isPhoneProject(info.project.name), "not_applicable: masaüstü motorlarında genişlik değiştirilerek çekilir");
  await page.setViewportSize({ width: 844, height: 390 });
  await page.goto("index.html");
  await settle(page);
  await expect(page).toHaveScreenshot("ozet-yatay-844.png");
  await page.setViewportSize({ width: 768, height: 1024 });
  await page.goto(SAMPLE_PROJECTS[1]);
  await settle(page);
  await expect(page).toHaveScreenshot("proje-tablet-768.png");
});

test("görsel: koyu tema özet 390 ve satır", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("index.html");
  await settle(page);
  await expect(page).toHaveScreenshot("ozet-koyu-390.png");
  await page.goto("siralama.html");
  await page.setViewportSize({ width: 390, height: 2400 });
  await expect(page.locator("#liste > li").first()).toHaveScreenshot("secenek-satiri-koyu-390.png");
});

test("görsel: şablon kapı bölümü 320 ve geniş ekranda kriter tanımları", async ({ page }, info) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.goto("sablon.html");
  const d = page.locator("#kapilar details").first();
  await d.evaluate((el) => { el.open = true; });
  await settle(page);
  await expect(d).toHaveScreenshot("sablon-kapi-320.png");
  test.skip(isPhoneProject(info.project.name), "not_applicable: geniş ekran masaüstü motorlarında");
  await page.setViewportSize({ width: 1280, height: 2400 });
  await expect(page.locator("#stratejik .crits")).toHaveScreenshot("sablon-stratejik-1280.png");
  const w = await page.locator("#stratejik .crit__why").first().evaluate((el) => el.getBoundingClientRect().width);
  expect(w, "kriter açıklaması geniş sütunda").toBeGreaterThan(500);
});

test("görsel: duyarlılık grafiği ve değer tablosu", async ({ page }, info) => {
  test.skip(isPhoneProject(info.project.name), "not_applicable: grafik masaüstü motorlarında karşılaştırılır");
  await page.setViewportSize({ width: 1280, height: 2400 });
  await page.goto("duyarlilik.html");
  await settle(page);
  await expect(page.locator(".figure svg")).toHaveScreenshot("duyarlilik-grafik-1280.png");
  await page.setViewportSize({ width: 390, height: 2400 });
  await expect(page.locator("#eksen .table-wrap")).toHaveScreenshot("duyarlilik-tablo-390.png");
});

test("görsel: klavye odağı düğmede ve bölüm gezintisi bağlantısında", async ({ page, browserName }, info) => {
  test.skip(isPhoneProject(info.project.name), "not_applicable: klavye denetimi masaüstü motorlarında yapılır");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("siralama.html");
  await page.locator("#suzgec-panel").evaluate((el) => { el.open = true; });
  const group = page.locator(".filters__group").first();
  const target = group.locator(".chip").nth(1);
  await target.focus();
  await page.keyboard.press(browserName === "webkit" ? "Alt+Shift+Tab" : "Shift+Tab");
  await page.keyboard.press(tabKey(browserName));
  await expect(target).toBeFocused();
  expect(await target.evaluate((el) => getComputedStyle(el).outlineStyle)).toBe("solid");
  await settle(page);
  await expect(group).toHaveScreenshot("odak-dugme-390.png");
  await page.goto("proje/qral.html");
  const link = page.locator(".toc__list a").nth(1);
  await page.locator(".toc__list a").first().focus();
  await page.keyboard.press(tabKey(browserName));
  await expect(link).toBeFocused();
  expect(await link.evaluate((el) => getComputedStyle(el).outlineStyle)).toBe("solid");
  await expect(page.locator(".toc")).toHaveScreenshot("odak-baglanti-390.png");
});

test("görsel: zorunlu renk kipi sıralama satırı 390", async ({ page }, info) => {
  test.skip(info.project.name !== "chromium", "not_run: zorunlu renk emülasyonu yalnız Chromium'da var");
  await page.emulateMedia({ forcedColors: "active" });
  await page.setViewportSize({ width: 390, height: 2400 });
  await page.goto("siralama.html");
  await settle(page);
  await expect(page.locator("#liste > li").first()).toHaveScreenshot("secenek-satiri-zorunlu-renk-390.png");
});

test("görsel: bulgular, yöntem katmanları ve alt bölüm 390", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 2400 });
  await page.goto("index.html");
  await settle(page);
  await expect(page.locator(".bigstats")).toHaveScreenshot("bulgular-390.png");
  await expect(page.locator(".layers")).toHaveScreenshot("katmanlar-390.png");
  await expect(page.locator(".site-footer")).toHaveScreenshot("alt-bolum-390.png");
});

test("görsel: geniş ekranda katman adımları, sıralama başı ve açık süzgeç paneli", async ({ page }, info) => {
  test.skip(isPhoneProject(info.project.name), "not_applicable: geniş ekran masaüstü motorlarında");
  await page.setViewportSize({ width: 1280, height: 2400 });
  await page.goto("sablon.html");
  await settle(page);
  await expect(page.locator(".layers")).toHaveScreenshot("katmanlar-1280.png");
  await page.goto("siralama.html");
  await page.locator("#suzgec-panel").evaluate((el) => { el.open = true; });
  await settle(page);
  await expect(page.locator(".masthead")).toHaveScreenshot("siralama-basi-1280.png");
  await expect(page.locator("#suzgec")).toHaveScreenshot("suzgec-acik-1280.png");
});

test("görsel: seçili dağılım düğmesi, eksi nakit ve ölçeği aşan nakit çizgisi 390", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 2400 });
  await page.goto("siralama.html");
  await settle(page);
  await page.locator('#dagilim button[data-karar="degistir"]').click();
  await expect(page.locator('#dagilim button[data-karar="degistir"]')).toHaveAttribute("aria-pressed", "true");
  await page.mouse.move(0, 0);
  await expect(page.locator(".page-head__fig")).toHaveScreenshot("dagilim-secili-390.png");
  await page.locator('#dagilim button[data-karar="degistir"]').click();
  await page.mouse.move(0, 0);
  const eksi = page.locator('#liste > li:has(.range[data-isaret="eksi"]) .metric--cash').first();
  await expect(eksi).toHaveScreenshot("nakit-eksi-390.png");
  const tasan = page.locator('#liste > li:has(.range[data-tasma]) .metric--cash').first();
  await expect(tasan).toHaveScreenshot("nakit-tasan-390.png");
  await page.goto("proje/qral.html");
  await settle(page);
  await expect(page.locator(".keyfacts")).toHaveScreenshot("proje-olculer-390.png");
});

test("görsel: koyu bantta klavye odağı (gezinme şeridi 320)", async ({ page, browserName }, info) => {
  test.skip(isPhoneProject(info.project.name), "not_applicable: klavye denetimi masaüstü motorlarında yapılır");
  await page.setViewportSize({ width: 320, height: 568 });
  await page.goto("index.html");
  const links = page.locator("#site-nav-list a");
  await links.first().focus();
  for (let i = 0; i < 5; i++) await page.keyboard.press(tabKey(browserName));
  await expect(links.nth(5)).toBeFocused();
  expect(await links.nth(5).evaluate((el) => getComputedStyle(el).outlineStyle)).toBe("solid");
  await expect(page.locator("#site-nav-list")).toHaveAttribute("data-kenar", "orta");
  await settle(page);
  await expect(page.locator(".site-header")).toHaveScreenshot("odak-serit-320.png");
});

test("görsel: üzerine gelme durumu (düğme, süzgeç düğmesi, gezinme bağlantısı, dağılım düğmesi)", async ({ page }, info) => {
  test.skip(isPhoneProject(info.project.name), "not_applicable: üzerine gelme ince işaretçili masaüstü motorlarında denetlenir");
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("index.html");
  await settle(page);
  const btn = page.locator(".cover .btn").first();
  const once = await btn.evaluate((el) => getComputedStyle(el).backgroundColor);
  await btn.hover();
  await expect.poll(() => btn.evaluate((el) => getComputedStyle(el).backgroundColor)).not.toBe(once);
  await expect(page.locator(".cover .btn-row")).toHaveScreenshot("uzerinde-dugme-1280.png");
  const nav = page.locator("#site-nav-list a").nth(2);
  await nav.hover();
  await expect(page.locator(".site-nav")).toHaveScreenshot("uzerinde-gezinme-1280.png");
  await page.goto("siralama.html");
  await settle(page);
  const hizli = page.locator('#dagilim button[data-karar="birak"]');
  await hizli.hover();
  await expect(page.locator("#dagilim")).toHaveScreenshot("uzerinde-dagilim-1280.png");
  await page.locator("#suzgec-panel > summary").click();
  const chip = page.locator('.chip[data-sort="puan"]');
  await chip.hover();
  await expect(page.locator(".filters__group").last()).toHaveScreenshot("uzerinde-suzgec-1280.png");
});

test("görsel: telefonda taşan tablo, kaydırılmış ve klavyeyle odaklanmış 390", async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 2400 });
  await page.goto("duyarlilik.html");
  await settle(page);
  const wrap = page.locator("#sira .table-wrap");
  await expect(wrap).toHaveAttribute("data-kenar", "bas");
  await expect(wrap).toHaveScreenshot("tablo-bas-390.png");
  await wrap.evaluate((w) => { w.scrollLeft = Math.round((w.scrollWidth - w.clientWidth) / 2); });
  await expect(wrap).toHaveAttribute("data-kenar", "orta");
  await expect(wrap).toHaveScreenshot("tablo-kaydirilmis-390.png");
  test.skip(isPhoneProject(info.project.name), "not_applicable: klavye odağı masaüstü motorlarında denetlenir");
  await wrap.evaluate((w) => { w.scrollLeft = 0; });
  await expect(wrap).toHaveAttribute("data-kenar", "bas");
  await wrap.focus();
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowLeft");
  await expect(wrap).toBeFocused();
  await expect(page.locator("#sira .wrap")).toHaveScreenshot("tablo-odak-390.png");
});
