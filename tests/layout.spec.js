// Yerleşim: 320 CSS px'ten başlayarak her kabul genişliğinde yatay taşma yok, kapalı içerik de ölçülür, kontroller dokunulabilir boyutta.
import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { ALL_PAGES, KEY_PAGES, VIEWPORTS, BREAKPOINTS, ROOT, INLINE_LINK, isPhoneProject, overflowReport, openAll, cssBreakpoints } from "./helpers.js";

const PHONE_MAX = 1024;

for (const url of ALL_PAGES) {
  test(`yerleşim: ${url} bütün kabul genişliklerinde, bölümler açıkken taşmıyor`, async ({ page }, info) => {
    const phone = isPhoneProject(info.project.name);
    await page.goto(url);
    await openAll(page);
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

test("yerleşim: 320 genişlikte menü açıkken de taşma yok", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  for (const url of KEY_PAGES) {
    await page.goto(url);
    await page.locator(".nav-toggle").click();
    await expect(page.locator("#site-nav-list")).toBeVisible();
    const r = await overflowReport(page);
    expect.soft(r.scrollWidth, `${url}: menü açık belge genişliği`).toBeLessThanOrEqual(r.clientWidth);
    expect.soft(r.disarida, `${url}: menü açık taşan öğe`).toEqual([]);
  }
});

test("kırılma noktaları stil dosyasıyla ve AGENTS.md ile aynı", async ({}, info) => {
  test.skip(info.project.name !== "chromium", "not_applicable: dosya düzeyi denetim tek projede yeterli");
  const css = cssBreakpoints();
  const agents = fs.readFileSync(path.join(ROOT, "AGENTS.md"), "utf8").match(/Kırılma noktaları: ([^.]+) rem/);
  expect(agents, "AGENTS.md kırılma noktası satırı").toBeTruthy();
  const doc = agents[1].replace(" ve ", ", ").split(",").map((x) => Number(x.trim()));
  expect(doc).toEqual(css);
});

for (const url of KEY_PAGES) {
  test(`kırılma noktaları: ${url} N−1, N, N+1 genişliklerinde taşmıyor`, async ({ page }, info) => {
    test.skip(isPhoneProject(info.project.name), "not_applicable: kırılma noktası taraması masaüstü motorlarında yapılır");
    await page.goto(url);
    await openAll(page);
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
    await openAll(page);
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

test("dokunma hedefleri: metin içi bağlantılar dışındaki bütün kontroller en az 44 CSS px", async ({ page }, info) => {
  const phone = isPhoneProject(info.project.name);
  if (!phone) await page.setViewportSize({ width: 320, height: 568 });
  for (const url of KEY_PAGES) {
    await page.goto(url);
    await openAll(page);
    const toggle = page.locator(".nav-toggle");
    if (await toggle.isVisible()) await toggle.click();
    const small = await page.evaluate((inline) => {
      const out = [];
      for (const el of document.querySelectorAll("a, button, summary, input")) {
        if (el.matches(inline) || el.closest(".skip-link, .skip-inline, svg")) continue;
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        const needW = el.matches("button, input") ? 44 : 24;
        if (r.height < 43.5 || r.width < needW - 0.5) out.push(`${el.tagName.toLowerCase()}.${el.className} ${r.width.toFixed(0)}×${r.height.toFixed(0)} "${el.textContent.trim().slice(0, 30)}"`);
      }
      return out.slice(0, 8);
    }, INLINE_LINK);
    expect.soft(small, `${url}: küçük dokunma hedefi`).toEqual([]);
  }
});

test("dokunma hedefleri: dokunmatik profilde bütün düğmeler 48 CSS px", async ({ page }, info) => {
  test.skip(!isPhoneProject(info.project.name), "not_applicable: yalnız dokunmatik telefon profilleri");
  for (const url of ["siralama.html", "projeler.html"]) {
    await page.goto(url);
    await openAll(page);
    const heights = await page.locator(".chip, .nav-toggle, .btn").evaluateAll((els) => els.filter((el) => el.getBoundingClientRect().height > 0).map((el) => el.getBoundingClientRect().height));
    expect(heights.length, `${url}: ölçülen düğme`).toBeGreaterThan(5);
    expect(Math.min(...heights), `${url}: en küçük düğme yüksekliği`).toBeGreaterThanOrEqual(47.5);
  }
});

test("kaydırma bölgeleri: taşan tablo adlandırılmış ve klavyeyle odaklanabilir", async ({ page }, info) => {
  test.skip(isPhoneProject(info.project.name), "not_applicable: klavye denetimi masaüstü motorlarında yapılır");
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

test.describe("metin uyarlamaları", () => {
  test.use({ bypassCSP: true });

  test("metin büyütme: 320 genişlikte yüzde 200 yazı, bölümler açıkken yatay taşma yok", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    for (const url of KEY_PAGES) {
      await page.goto(url);
      await openAll(page);
      await page.addStyleTag({ content: "html{font-size:200%}" });
      const r = await overflowReport(page);
      expect.soft(r.scrollWidth, `${url}: yüzde 200 yazıda belge genişliği`).toBeLessThanOrEqual(r.clientWidth);
    }
  });

  test("metin aralığı (WCAG 1.4.12): 320 genişlikte taşma ve kırpılma yok", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    for (const url of KEY_PAGES) {
      await page.goto(url);
      await openAll(page);
      await page.addStyleTag({ content: "*{line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important}p{margin-bottom:2em!important}" });
      const r = await overflowReport(page);
      expect.soft(r.scrollWidth, `${url}: metin aralığında belge genişliği`).toBeLessThanOrEqual(r.clientWidth);
      const clipped = await page.evaluate(() => [...document.querySelectorAll("p, li, dd, dt, h1, h2, h3, summary, .tag, .chip, .btn")]
        .filter((el) => { const cs = getComputedStyle(el); return !el.closest(".visually-hidden") && el.getBoundingClientRect().height > 0 && cs.overflow === "hidden" && el.scrollHeight > el.clientHeight + 1; })
        .map((el) => el.tagName + "." + el.className).slice(0, 5));
      expect.soft(clipped, `${url}: kırpılan metin`).toEqual([]);
    }
  });
});

test("düzen kayması: yavaş ağda ilk yüklemede menü ve içerik kaymıyor (CLS)", async ({ page }, info) => {
  test.skip(!["chromium", "telefon-chromium"].includes(info.project.name), "not_run: layout-shift ölçümü ve ağ yavaşlatma yalnız Chromium'da var");
  await page.setViewportSize({ width: 320, height: 568 });
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Network.enable");
  await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 300, downloadThroughput: 40 * 1024, uploadThroughput: 40 * 1024 });
  for (const url of ["index.html", "proje/qral.html"]) {
    await page.goto(url, { waitUntil: "load" });
    const cls = await page.evaluate(() => new Promise((res) => {
      let v = 0;
      new PerformanceObserver((l) => { for (const e of l.getEntries()) if (!e.hadRecentInput) v += e.value; }).observe({ type: "layout-shift", buffered: true });
      setTimeout(() => res(v), 600);
    }));
    expect.soft(cls, `${url}: toplam düzen kayması`).toBeLessThan(0.02);
  }
});
