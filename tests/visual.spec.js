// Görsel regresyon: sabit ortamda (aynı makine, aynı motor sürümü) deterministik karşılaştırma.
// Referanslar tests/__snapshots__/<platform>/<proje>/ altındadır; yeni referans ancak önce/sonra farkı incelenerek kabul edilir.
import { test, expect } from "@playwright/test";
import { SAMPLE_PROJECTS, isPhoneProject } from "./helpers.js";

const SIZES = [{ ad: "320", width: 320, height: 568 }, { ad: "390", width: 390, height: 844 }, { ad: "1280", width: 1280, height: 800 }];

async function settle(page) {
  await page.evaluate(() => document.fonts.ready);
}

for (const size of SIZES) {
  test(`görsel: özet ${size.ad}`, async ({ page }, info) => {
    test.skip(isPhoneProject(info.project.name) && size.width > 400, "telefon profili yalnız telefon genişliklerinde");
    await page.setViewportSize({ width: size.width, height: size.height });
    await page.goto("index.html");
    await settle(page);
    await expect(page).toHaveScreenshot(`ozet-${size.ad}.png`);
  });

  test(`görsel: sıralama ${size.ad}`, async ({ page }, info) => {
    test.skip(isPhoneProject(info.project.name) && size.width > 400, "telefon profili yalnız telefon genişliklerinde");
    await page.setViewportSize({ width: size.width, height: size.height });
    await page.goto("siralama.html");
    await page.locator("#suzgec-panel").evaluate((el) => { el.open = true; });
    await settle(page);
    await expect(page).toHaveScreenshot(`siralama-${size.ad}.png`);
    await expect(page.locator("#liste > li").first()).toHaveScreenshot(`secenek-satiri-${size.ad}.png`);
  });

  test(`görsel: proje sayfası ${size.ad}`, async ({ page }, info) => {
    test.skip(isPhoneProject(info.project.name) && size.width > 400, "telefon profili yalnız telefon genişliklerinde");
    await page.setViewportSize({ width: size.width, height: size.height });
    await page.goto(SAMPLE_PROJECTS[1]);
    await settle(page);
    await expect(page).toHaveScreenshot(`proje-${size.ad}.png`);
    // Öğe görüntüleri için görünüm alanı uzatılır (genişlik aynı kalır, yerleşim değişmez): görünüm alanına sığmayan öğenin alt kısmı kırpılmasın.
    await page.setViewportSize({ width: size.width, height: 2400 });
    const first = page.locator("main section.section").nth(2);
    await first.locator("details").first().evaluate((el) => { el.open = true; });
    await expect(first.locator(".gates")).toHaveScreenshot(`kapilar-${size.ad}.png`);
    await expect(first.locator(".crits").first()).toHaveScreenshot(`kriterler-${size.ad}.png`);
  });
}

test("görsel: koyu tema özet 390", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("index.html");
  await settle(page);
  await expect(page).toHaveScreenshot("ozet-koyu-390.png");
});

test("görsel: koyu tema sıralama satırı", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("siralama.html");
  await settle(page);
  await expect(page.locator("#liste > li").first()).toHaveScreenshot("secenek-satiri-koyu-390.png");
});

test("görsel: şablon sayfası açık kapı bölümü 320", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.goto("sablon.html");
  const d = page.locator("#kapilar details").first();
  await d.evaluate((el) => { el.open = true; });
  await settle(page);
  await expect(d).toHaveScreenshot("sablon-kapi-320.png");
});

test("görsel: duyarlılık grafiği", async ({ page }, info) => {
  test.skip(isPhoneProject(info.project.name), "grafik masaüstü motorlarında karşılaştırılır");
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("duyarlilik.html");
  await settle(page);
  await expect(page.locator(".figure svg")).toHaveScreenshot("duyarlilik-grafik-1280.png");
});

test("görsel: klavye odağı düğmede", async ({ page, browserName }, info) => {
  test.skip(isPhoneProject(info.project.name), "klavye denetimi masaüstü motorlarında yapılır");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("siralama.html");
  await page.locator("#suzgec-panel").evaluate((el) => { el.open = true; });
  const group = page.locator(".filters__group").first();
  const target = group.locator(".chip").nth(1);
  // macOS WebKit'te Tab yalnız form alanlarında durur; düğmeler Option+Tab ile gezilir.
  const fwd = browserName === "webkit" ? "Alt+Tab" : "Tab";
  const back = browserName === "webkit" ? "Alt+Shift+Tab" : "Shift+Tab";
  await target.focus();
  await page.keyboard.press(back);
  await page.keyboard.press(fwd);
  // Ekran görüntüsünden önce odağın gerçekten düğmede ve görünür olduğu doğrulanır; odaksız bir referans kaydedilemez.
  await expect(target).toBeFocused();
  expect(await target.evaluate((el) => getComputedStyle(el).outlineStyle)).toBe("solid");
  await settle(page);
  await expect(group).toHaveScreenshot("odak-dugme-390.png");
});

test("görsel: zorunlu renk kipi sıralama 390", async ({ page }, info) => {
  test.skip(info.project.name !== "chromium", "zorunlu renk emülasyonu Chromium'da yapılır");
  await page.emulateMedia({ forcedColors: "active" });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("siralama.html");
  await settle(page);
  await expect(page.locator("#liste > li").first()).toHaveScreenshot("secenek-satiri-zorunlu-renk-390.png");
});
