// Erişilebilirlik: axe (ihlaller ve izin listesi dışındaki eksik sonuçlar), belge yapısı, token karşıtlığı, azaltılmış hareket, zorunlu renk, yazdırma.
import { test, expect } from "@playwright/test";
import * as axePkg from "@axe-core/playwright";
import fs from "node:fs";
import path from "node:path";
import { ALL_PAGES, KEY_PAGES, DOCS, ROOT, isPhoneProject, openAll } from "./helpers.js";

const AxeBuilder = axePkg.AxeBuilder || axePkg.default?.AxeBuilder || axePkg.default;
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"];
// axe'nin kendi başına karar veremediği ve gerekçesi bilinen durumlar. Liste dışındaki her "incomplete" sonuç test hatasıdır.
const INCOMPLETE_ALLOW = {
  "color-contrast": "taralı puan çubukları ve yarı dolu işaretler gradyan; axe arka planı hesaplayamaz. Token karşıtlığı ayrı testte ölçülüyor.",
};

async function axe(page) {
  const res = await new AxeBuilder({ page }).withTags(TAGS).analyze();
  const v = res.violations.map((x) => `${x.id} (${x.impact}): ${x.nodes.length} öğe; örnek ${x.nodes[0].target.join(" ")}`);
  const inc = res.incomplete.filter((x) => !INCOMPLETE_ALLOW[x.id]).map((x) => `eksik ${x.id}: ${x.nodes.length} öğe; örnek ${x.nodes[0].target.join(" ")}`);
  return [...v, ...inc];
}

for (const scheme of ["light", "dark"]) {
  for (const url of KEY_PAGES) {
    test(`axe: ${url} (${scheme})`, async ({ page }, info) => {
      test.skip(scheme === "dark" && info.project.name !== "chromium" && info.project.name !== "telefon-webkit", "not_run: koyu tema axe denetimi iki profilde koşar");
      await page.emulateMedia({ colorScheme: scheme });
      await page.goto(url);
      await openAll(page);
      const toggle = page.locator(".nav-toggle");
      if (await toggle.isVisible()) await toggle.click();
      expect(await axe(page)).toEqual([]);
    });
  }
}

test("axe: süzgeç uygulanmış ve boş durum", async ({ page }) => {
  await page.goto("siralama.html");
  await page.locator("#q").fill("zzzzqqqq-yok");
  await expect(page.locator("#bos")).toBeVisible();
  expect(await axe(page)).toEqual([]);
});

test.describe("belge yapısı", () => {
  test.beforeEach(async ({}, info) => {
    test.skip(info.project.name !== "chromium", "not_applicable: dosya düzeyi denetim tek projede yeterli");
  });

  test("her sayfada dil, tek ana başlık, sıralı başlıklar ve adlandırılmış bölgeler var", async () => {
    const problems = [];
    for (const rel of [...ALL_PAGES, "404.html"]) {
      const html = fs.readFileSync(path.join(DOCS, rel), "utf8");
      if (!/<html lang="tr">/.test(html)) problems.push(`${rel}: lang eksik`);
      if ((html.match(/<h1[\s>]/g) || []).length !== 1) problems.push(`${rel}: h1 sayısı`);
      const levels = [...html.matchAll(/<h([1-6])[\s>]/g)].map((m) => Number(m[1]));
      for (let i = 1; i < levels.length; i++) if (levels[i] - levels[i - 1] > 1) { problems.push(`${rel}: başlık düzeyi atlıyor h${levels[i - 1]} → h${levels[i]}`); break; }
      for (const tag of ["<header", "<main", "<footer"]) if (!html.includes(tag)) problems.push(`${rel}: ${tag} yok`);
      for (const m of html.matchAll(/<nav([^>]*)>/g)) if (!/aria-label="[^"]+"/.test(m[1])) problems.push(`${rel}: adsız nav`);
      for (const m of html.matchAll(/<svg([^>]*)>/g)) if (!/aria-labelledby=|aria-label=|aria-hidden="true"/.test(m[1])) problems.push(`${rel}: adsız svg`);
      for (const m of html.matchAll(/<(div|span)([^>]*)aria-label=/g)) if (!/role="/.test(m[2])) problems.push(`${rel}: rolsüz ${m[1]} üzerinde aria-label`);
      const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]);
      const dup = ids.filter((x, i) => ids.indexOf(x) !== i);
      if (dup.length) problems.push(`${rel}: yinelenen id ${[...new Set(dup)].slice(0, 3).join(", ")}`);
      if (!/<title>[^<]{3,}<\/title>/.test(html)) problems.push(`${rel}: başlık etiketi eksik`);
      if (!/<meta name="description" content="[^"]{10,}"/.test(html)) problems.push(`${rel}: açıklama eksik`);
    }
    expect(problems).toEqual([]);
  });

  test("sayfa başlıkları birbirinden farklı", async () => {
    const titles = ALL_PAGES.map((rel) => fs.readFileSync(path.join(DOCS, rel), "utf8").match(/<title>([^<]*)<\/title>/)[1]);
    expect(new Set(titles).size).toBe(titles.length);
  });

  test("emoji yok", async () => {
    const rx = /[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\u{1F1E6}-\u{1F1FF}]/u;
    const hits = [];
    for (const rel of [...ALL_PAGES, "404.html"]) {
      const m = fs.readFileSync(path.join(DOCS, rel), "utf8").match(rx);
      if (m) hits.push(`${rel}: U+${m[0].codePointAt(0).toString(16)}`);
    }
    expect(hits).toEqual([]);
  });

  test("stil dosyaları: bileşenlerde sabit renk ve piksel değeri yok (tokenlar dışında)", async () => {
    const bad = [];
    for (const f of ["base.css", "components.css"]) {
      const css = fs.readFileSync(path.join(ROOT, "src", "styles", f), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
      for (const m of css.matchAll(/#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(|-?\d*\.?\d+px\b/g)) bad.push(`${f}: ${m[0]}`);
    }
    expect(bad).toEqual([]);
  });
});

function tokens() {
  const css = fs.readFileSync(path.join(ROOT, "src", "styles", "tokens.css"), "utf8");
  const light = css.slice(css.indexOf(":root"), css.indexOf("@media (any-pointer"));
  const dark = css.slice(css.indexOf("@media (prefers-color-scheme: dark)"), css.indexOf("@media (forced-colors"));
  const read = (block) => Object.fromEntries([...block.matchAll(/(--c-[a-z0-9-]+):\s*(#[0-9a-fA-F]{6})/g)].map((m) => [m[1], m[2]]));
  const l = read(light);
  return { light: l, dark: { ...l, ...read(dark) } };
}
const lum = (hex) => {
  const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255).map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
};
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

test("token karşıtlığı: metin 4,5:1, odak göstergesi ve grafik parçalar 3:1", async ({}, info) => {
  test.skip(info.project.name !== "chromium", "not_applicable: dosya düzeyi denetim tek projede yeterli");
  const t = tokens();
  const TEXT = [["--c-ink", "--c-paper"], ["--c-ink-2", "--c-paper"], ["--c-muted", "--c-paper"], ["--c-brand", "--c-paper"], ["--c-ink", "--c-surface"], ["--c-ink-2", "--c-surface"],
    ["--c-muted", "--c-surface"], ["--c-brand", "--c-surface"], ["--c-ink-2", "--c-sunken"], ["--c-muted", "--c-sunken"], ["--c-ink", "--c-band"], ["--c-ink-2", "--c-band"], ["--c-muted", "--c-band"],
    ["--c-brand", "--c-band"], ["--c-ok", "--c-ok-soft"], ["--c-test", "--c-test-soft"], ["--c-fail", "--c-fail-soft"], ["--c-brand", "--c-brand-soft"], ["--c-ok", "--c-paper"],
    ["--c-test", "--c-paper"], ["--c-fail", "--c-paper"], ["--c-brand-ink", "--c-brand"], ["--c-paper", "--c-ink"]];
  const GRAPHIC = [["--c-focus", "--c-paper"], ["--c-focus", "--c-surface"], ["--c-focus", "--c-sunken"], ["--c-focus", "--c-band"], ["--c-line-strong", "--c-paper"], ["--c-line-strong", "--c-surface"],
    ["--c-meter-proven", "--c-sunken"], ["--c-meter-claim", "--c-sunken"], ["--c-meter-proven", "--c-meter-claim"]];
  const low = [];
  for (const scheme of ["light", "dark"]) {
    for (const [fg, bg] of TEXT) { const r = ratio(t[scheme][fg], t[scheme][bg]); if (r < 4.5) low.push(`${scheme} metin ${fg} / ${bg}: ${r.toFixed(2)}`); }
    for (const [fg, bg] of GRAPHIC) { const r = ratio(t[scheme][fg], t[scheme][bg]); if (r < 3) low.push(`${scheme} grafik ${fg} / ${bg}: ${r.toFixed(2)}`); }
  }
  expect(low).toEqual([]);
});

test("azaltılmış hareket: sonradan eklenen geçiş de etkisizleşir", async ({ page }) => {
  await page.goto("siralama.html");
  const sure = (reduce) => page.evaluate(() => {
    const el = document.querySelector(".opt");
    el.style.transition = "opacity 1s";
    return parseFloat(getComputedStyle(el).transitionDuration);
  });
  expect(await sure()).toBeGreaterThan(0.5);
  await page.emulateMedia({ reducedMotion: "reduce" });
  expect(await sure()).toBeLessThan(0.01);
});

test("zorunlu renk kipi: puan çubuğu ve huni çizili, seçili düğme ayırt ediliyor, karar etiketi metin renginde", async ({ page }, info) => {
  test.skip(info.project.name !== "chromium", "not_run: zorunlu renk emülasyonu yalnız Chromium'da var");
  await page.emulateMedia({ forcedColors: "active" });
  await page.goto("index.html");
  expect(await page.locator(".funnel__bar").first().evaluate((el) => getComputedStyle(el).outlineStyle)).toBe("solid");
  await page.goto("siralama.html");
  const m = await page.locator(".meter").first().evaluate((el) => ({ outline: getComputedStyle(el).outlineStyle, proven: getComputedStyle(el.querySelector(".meter__proven")).backgroundColor, canvas: getComputedStyle(document.body).backgroundColor }));
  expect(m.outline).toBe("solid");
  expect(m.proven).not.toBe(m.canvas);
  const tagColor = await page.locator(".tag").first().evaluate((el) => getComputedStyle(el).color);
  const textColor = await page.evaluate(() => getComputedStyle(document.body).color);
  expect(tagColor).toBe(textColor);
  await page.locator("#suzgec-panel").evaluate((el) => { el.open = true; });
  const on = await page.locator('.chip[aria-pressed="true"]').first().evaluate((el) => getComputedStyle(el).backgroundColor);
  const off = await page.locator('.chip[aria-pressed="false"]').first().evaluate((el) => getComputedStyle(el).backgroundColor);
  expect(on).not.toBe(off);
});

test("durum yalnız renkle anlatılmıyor: kapı ve karar işaretlerinin görünür metni var", async ({ page }, info) => {
  test.skip(isPhoneProject(info.project.name), "not_applicable: tek profil yeterli");
  await page.goto("siralama.html");
  const row = page.locator("#liste > li").first();
  await expect(row.locator(".tag")).not.toBeEmpty();
  for (const w of ["geçti", "test", "kaldı"]) await expect(row.locator(".gsum")).toContainText(w);
  const visibleText = await row.locator(".gsum__part").first().evaluate((el) => el.getBoundingClientRect().width > 20);
  expect(visibleText).toBe(true);
  await page.goto("proje/qral.html");
  await openAll(page);
  await expect(page.locator(".ev-legend").first()).toContainText("E0");
});

test("yazdırma: gezinme gizli, renkler açık tema", async ({ page }, info) => {
  test.skip(info.project.name !== "chromium", "not_applicable: tek projede yeterli");
  await page.emulateMedia({ media: "print", colorScheme: "dark" });
  await page.goto("proje/qral.html");
  await expect(page.locator(".toc")).toBeHidden();
  const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  expect(bg).toBe("rgb(255, 255, 255)");
});
