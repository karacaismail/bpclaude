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
    await page.locator("#suzgec-panel").evaluate((el) => { el.open = true; });
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

test("görsel: menü açık 320", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.goto("index.html");
  await page.locator(".nav-toggle").click();
  await settle(page);
  await expect(page.locator(".site-header")).toHaveScreenshot("menu-acik-320.png");
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
