// Yerleşim: 320 CSS px'ten başlayarak her kabul genişliğinde yatay taşma yok, içerik ekranda, kontroller dokunulabilir boyutta.
import { test, expect } from "@playwright/test";
import { ALL_PAGES, KEY_PAGES, VIEWPORTS, BREAKPOINTS, isPhoneProject, overflowReport } from "./helpers.js";

const PHONE_MAX = 1024;

for (const url of ALL_PAGES) {
  test(`yerleşim: ${url} bütün kabul genişliklerinde taşmıyor`, async ({ page }, info) => {
    const phone = isPhoneProject(info.project.name);
    await page.goto(url);
    for (const vp of VIEWPORTS) {
      if (phone && vp.width > PHONE_MAX) continue;
      await page.setViewportSize({ width: vp.width, height: vp.height });
      const r = await overflowReport(page);
      expect.soft(r.scrollWidth, `${url} @${vp.ad}: belge genişliği`).toBeLessThanOrEqual(r.clientWidth);
      expect.soft(r.disarida, `${url} @${vp.ad}: ekran dışına taşan öğe`).toEqual([]);
      await expect.soft(page.locator("h1"), `${url} @${vp.ad}: başlık görünür`).toBeVisible();
    }
  });
}

for (const url of KEY_PAGES) {
  test(`kırılma noktaları: ${url} N−1, N, N+1 genişliklerinde taşmıyor`, async ({ page }, info) => {
    test.skip(isPhoneProject(info.project.name), "kırılma noktası taraması masaüstü motorlarında yapılır");
    await page.goto(url);
    for (const bp of BREAKPOINTS) {
      for (const w of [bp - 1, bp, bp + 1]) {
        await page.setViewportSize({ width: w, height: 800 });
        const r = await overflowReport(page);
        expect.soft(r.scrollWidth, `${url} @${w}px: belge genişliği`).toBeLessThanOrEqual(r.clientWidth);
        expect.soft(r.disarida, `${url} @${w}px: ekran dışına taşan öğe`).toEqual([]);
      }
    }
  });
}

test("yerleşim: 320 genişlikte en küçük yazı 13 pikselin altına inmiyor", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  for (const url of KEY_PAGES) {
    await page.goto(url);
    const min = await page.evaluate(() => {
      let m = 99;
      const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (w.nextNode()) {
        const n = w.currentNode;
        if (!n.textContent.trim()) continue;
        const el = n.parentElement;
        if (!el || el.closest("svg, script, style, .visually-hidden")) continue;
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        m = Math.min(m, parseFloat(getComputedStyle(el).fontSize));
      }
      return m;
    });
    expect.soft(min, `${url}: en küçük yazı boyutu`).toBeGreaterThanOrEqual(12.9);
  }
});

test("dokunma hedefleri: kontroller en az 44 CSS px yüksekliğinde", async ({ page }, info) => {
  const phone = isPhoneProject(info.project.name);
  await page.setViewportSize(phone ? page.viewportSize() : { width: 320, height: 568 });
  const sel = ".nav-toggle, .site-nav a, .chip, .btn, summary, .field input, .linklist a, .pager a, .anchor-nav a, .brand, .opt__title a";
  for (const url of KEY_PAGES) {
    await page.goto(url);
    const toggle = page.locator(".nav-toggle");
    if (await toggle.isVisible()) await toggle.click();
    const small = await page.evaluate((s) => {
      const out = [];
      for (const el of document.querySelectorAll(s)) {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        const needW = el.matches(".chip, .btn, .nav-toggle") ? 44 : 24;
        if (r.height < 43.5 || r.width < needW - 0.5) out.push(`${el.tagName.toLowerCase()}.${el.className} ${r.width.toFixed(0)}×${r.height.toFixed(0)} "${el.textContent.trim().slice(0, 30)}"`);
      }
      return out.slice(0, 8);
    }, sel);
    expect.soft(small, `${url}: küçük dokunma hedefi`).toEqual([]);
  }
});

test("dokunma hedefleri: dokunmatik profilde kontroller 48 CSS px", async ({ page }, info) => {
  test.skip(!isPhoneProject(info.project.name), "yalnız dokunmatik telefon profilleri");
  await page.goto("siralama.html");
  await page.locator("#suzgec-panel > summary").click();
  const h = await page.locator(".chip").first().evaluate((el) => el.getBoundingClientRect().height);
  expect(h).toBeGreaterThanOrEqual(47.5);
});

test("kaydırma bölgeleri: taşan tablo adlandırılmış ve klavyeyle odaklanabilir", async ({ page }, info) => {
  test.skip(isPhoneProject(info.project.name), "klavye denetimi masaüstü motorlarında yapılır");
  await page.setViewportSize({ width: 320, height: 568 });
  for (const url of ["duyarlilik.html", "portfoy.html", "sablon.html", "hakkinda.html"]) {
    await page.goto(url);
    const regions = await page.evaluate(() => [...document.querySelectorAll(".table-wrap, .figure__scroll")].map((r) => ({
      tasiyor: r.scrollWidth > r.clientWidth, tabindex: r.getAttribute("tabindex"), rol: r.getAttribute("role"), ad: r.getAttribute("aria-label"),
    })));
    expect(regions.length, `${url}: kaydırma bölgesi var`).toBeGreaterThan(0);
    for (const r of regions) {
      expect.soft(r.rol, `${url}: bölge rolü`).toBe("region");
      expect.soft(r.ad, `${url}: bölge adı`).toBeTruthy();
      expect.soft(r.tabindex, `${url}: taşan bölge odaklanabilir, taşmayan odak durağı değil`).toBe(r.tasiyor ? "0" : null);
    }
  }
  await page.goto("duyarlilik.html");
  const region = page.locator(".table-wrap[tabindex='0']").first();
  await region.focus();
  const before = await region.evaluate((el) => el.scrollLeft);
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowRight");
  await expect.poll(() => region.evaluate((el) => el.scrollLeft)).toBeGreaterThan(before);
});

test("metin büyütme: 320 genişlikte yüzde 200 yazı boyutunda yatay taşma yok", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  for (const url of KEY_PAGES) {
    await page.goto(url);
    await page.addStyleTag({ content: "html{font-size:200%}" });
    const r = await overflowReport(page);
    expect.soft(r.scrollWidth, `${url}: yüzde 200 yazıda belge genişliği`).toBeLessThanOrEqual(r.clientWidth);
  }
});
