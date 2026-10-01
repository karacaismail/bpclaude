// Ağ ve bütünlük: dış istek yok, kırık bağlantı yok, konsol temiz, boyut bütçesi içinde, 404 sayfası her derinlikte biçimli.
import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { ALL_PAGES, KEY_PAGES, DOCS, isPhoneProject } from "./helpers.js";

// Proje bütçesi (gzip, bayt). Ölçüm koşulu: docs/ altındaki dosyanın gzip -9 boyutu. Tek profil vardır; koşullu paket yoktur.
const BUDGET = { css: 8 * 1024, js: 4 * 1024, html: 64 * 1024, ilkYuk: 80 * 1024 };
const gz = (file) => zlib.gzipSync(fs.readFileSync(file), { level: 9 }).length;

test.describe("statik bütünlük", () => {
  test.beforeEach(async ({}, info) => {
    test.skip(info.project.name !== "chromium", "dosya düzeyi denetim tek projede yeterli");
  });

  test("iç bağlantılar ve çapalar çözülüyor", async () => {
    const broken = [];
    const idCache = new Map();
    const idsOf = (file) => {
      if (!idCache.has(file)) idCache.set(file, new Set([...fs.readFileSync(file, "utf8").matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
      return idCache.get(file);
    };
    for (const rel of [...ALL_PAGES, "404.html"]) {
      const file = path.join(DOCS, rel);
      const html = fs.readFileSync(file, "utf8");
      for (const m of html.matchAll(/\s(?:href|src)="([^"]+)"/g)) {
        const ref = m[1];
        if (/^(mailto:|tel:|data:)/.test(ref)) { broken.push(`${rel}: beklenmeyen şema ${ref}`); continue; }
        if (/^(https?:)?\/\//.test(ref)) { broken.push(`${rel}: dış bağlantı ${ref}`); continue; }
        const [p, hash] = ref.split("#");
        let target = file;
        if (p) target = p.startsWith("/bpclaude/") ? path.join(DOCS, p.slice("/bpclaude/".length)) : path.resolve(path.dirname(file), p);
        if (!fs.existsSync(target)) { broken.push(`${rel}: dosya yok ${ref}`); continue; }
        if (hash && target.endsWith(".html") && !idsOf(target).has(hash)) broken.push(`${rel}: çapa yok ${ref}`);
      }
    }
    expect(broken).toEqual([]);
  });

  test("boyut bütçesi: stil, betik ve sayfalar sınırın altında", async () => {
    const css = gz(path.join(DOCS, "assets", "site.css"));
    const js = gz(path.join(DOCS, "assets", "site.js"));
    expect.soft(css, "site.css gzip").toBeLessThanOrEqual(BUDGET.css);
    expect.soft(js, "site.js gzip").toBeLessThanOrEqual(BUDGET.js);
    for (const rel of ALL_PAGES) {
      const h = gz(path.join(DOCS, rel));
      expect.soft(h, `${rel} gzip`).toBeLessThanOrEqual(BUDGET.html);
      expect.soft(h + css + js, `${rel} ilk yük gzip`).toBeLessThanOrEqual(BUDGET.ilkYuk);
    }
  });

  test("her sayfada tek stil ve tek betik dosyası var; satır içi betik yok", async () => {
    for (const rel of ALL_PAGES) {
      const html = fs.readFileSync(path.join(DOCS, rel), "utf8");
      expect.soft((html.match(/<link rel="stylesheet"/g) || []).length, `${rel}: stil dosyası`).toBe(1);
      expect.soft((html.match(/<script /g) || []).length, `${rel}: betik dosyası`).toBe(1);
      expect.soft(/<script>|<script(?![^>]*\ssrc=)/.test(html), `${rel}: satır içi betik`).toBe(false);
      expect.soft(/\son[a-z]+="/.test(html), `${rel}: satır içi olay işleyici`).toBe(false);
      expect.soft(html.includes('http-equiv="Content-Security-Policy"'), `${rel}: içerik güvenlik politikası`).toBe(true);
      expect.soft(html.includes('name="robots" content="noindex, nofollow"'), `${rel}: noindex`).toBe(true);
    }
    expect(fs.readFileSync(path.join(DOCS, "robots.txt"), "utf8")).toContain("Disallow: /");
  });

  test("indirilecek dosyalar yerinde ve boş değil", async ({ request }) => {
    for (const [name, magic] of [["bpclaude-secim-sablonu.xlsx", "PK"], ["bpclaude-secenekler.csv", null], ["bpclaude-model.json", "{"]]) {
      const res = await request.get(`indir/${name}`);
      expect(res.status(), name).toBe(200);
      const body = await res.body();
      expect(body.length, `${name} boyutu`).toBeGreaterThan(1000);
      if (magic) expect(body.subarray(0, magic.length).toString("latin1"), `${name} biçimi`).toBe(magic);
    }
    const data = JSON.parse(fs.readFileSync(path.join(DOCS, "indir", "bpclaude-model.json"), "utf8"));
    expect(data.secenekler.length).toBeGreaterThan(100);
  });
});

for (const url of KEY_PAGES) {
  test(`ağ: ${url} yalnız kendi kaynaklarını yükler, konsol temiz`, async ({ page, baseURL }) => {
    const origin = new URL(baseURL).origin;
    const external = [];
    const failed = [];
    const consoleMsgs = [];
    const requests = [];
    page.on("request", (r) => { requests.push(r.url()); if (!r.url().startsWith(origin)) external.push(r.url()); });
    page.on("response", (r) => { if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`); });
    page.on("console", (m) => { if (["error", "warning"].includes(m.type())) consoleMsgs.push(`${m.type()}: ${m.text()}`); });
    page.on("pageerror", (e) => consoleMsgs.push(`hata: ${e.message}`));
    await page.goto(url, { waitUntil: "networkidle" });
    expect.soft(external, "dış istek").toEqual([]);
    expect.soft(failed, "başarısız istek").toEqual([]);
    expect.soft(consoleMsgs, "konsol iletisi").toEqual([]);
    // Tek profil: belge, bir stil dosyası, bir betik. Koşullu ya da gizlenmiş ek paket indirilmez.
    const kinds = requests.map((u) => new URL(u).pathname.split("/").pop().split(".").pop());
    expect.soft(kinds.filter((k) => k === "css").length, "stil isteği").toBe(1);
    expect.soft(kinds.filter((k) => k === "js").length, "betik isteği").toBe(1);
    expect.soft(requests.length, `istek sayısı: ${requests.join(", ")}`).toBeLessThanOrEqual(4);
  });
}

test("404: iç içe bulunmayan adreste sayfa biçimli ve bağlantıları çalışır", async ({ page, baseURL }, info) => {
  test.skip(isPhoneProject(info.project.name), "tek profil yeterli");
  const res = await page.goto("proje/boyle-bir-sayfa-yok/derin.html");
  expect(res.status()).toBe(404);
  await expect(page.locator("h1")).toHaveText("Bu sayfa yok");
  const bg = await page.evaluate(() => getComputedStyle(document.body).fontFamily);
  expect(bg, "stil dosyası yüklendi").toContain("apple-system");
  await page.locator("a.btn", { hasText: "Özete dön" }).click();
  await expect(page).toHaveURL(new URL("index.html", baseURL).href);
  await expect(page.locator("h1")).toBeVisible();
});

test("içerik güvenlik politikası satır içi betiği engelliyor", async ({ page }, info) => {
  test.skip(info.project.name !== "chromium", "tek projede yeterli");
  const violations = [];
  page.on("console", (m) => { if (m.text().includes("Content Security Policy")) violations.push(m.text()); });
  await page.goto("index.html");
  const ran = await page.evaluate(() => {
    const s = document.createElement("script");
    s.textContent = "window.__inline = true";
    document.head.appendChild(s);
    return window.__inline === true;
  });
  expect(ran, "satır içi betik çalışmamalı").toBe(false);
  expect(violations.length).toBeGreaterThan(0);
});
