// Ağ ve bütünlük: dış istek yok, kırık bağlantı yok, konsol temiz, boyut bütçesi içinde, 404 sayfası her derinlikte biçimli.
import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { ALL_PAGES, KEY_PAGES, DOCS, isPhoneProject } from "./helpers.js";

// Proje bütçesi (gzip, bayt). Ölçüm koşulu: docs/ altındaki dosyanın gzip -9 boyutu. Tek profil vardır; koşullu paket yoktur.
const BUDGET = { css: 8 * 1024, js: 4 * 1024, html: 64 * 1024, ilkYuk: 80 * 1024 };
const gz = (file) => zlib.gzipSync(fs.readFileSync(file), { level: 9 }).length;
const HTML_ALL = [...ALL_PAGES, "404.html"];

test.describe("statik bütünlük", () => {
  test.beforeEach(async ({}, info) => {
    test.skip(info.project.name !== "chromium", "not_applicable: dosya düzeyi denetim tek projede yeterli");
  });

  test("iç bağlantılar ve çapalar çözülüyor", async () => {
    const broken = [];
    const idCache = new Map();
    const idsOf = (file) => {
      if (!idCache.has(file)) idCache.set(file, new Set([...fs.readFileSync(file, "utf8").matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
      return idCache.get(file);
    };
    for (const rel of HTML_ALL) {
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
    test.info().annotations.push({ type: "olcum", description: `site.css ${css} B, site.js ${js} B (gzip -9)` });
    expect.soft(css, "site.css gzip").toBeLessThanOrEqual(BUDGET.css);
    expect.soft(js, "site.js gzip").toBeLessThanOrEqual(BUDGET.js);
    let enBuyuk = ["", 0];
    for (const rel of HTML_ALL) {
      const h = gz(path.join(DOCS, rel));
      if (h > enBuyuk[1]) enBuyuk = [rel, h];
      expect.soft(h, `${rel} gzip`).toBeLessThanOrEqual(BUDGET.html);
      expect.soft(h + css + js, `${rel} ilk yük gzip`).toBeLessThanOrEqual(BUDGET.ilkYuk);
    }
    test.info().annotations.push({ type: "olcum", description: `en büyük sayfa ${enBuyuk[0]} ${enBuyuk[1]} B (gzip -9)` });
  });

  test("her sayfada (404 dahil) tek stil, tek betik, güvenlik politikası ve noindex var; satır içi betik yok", async () => {
    for (const rel of HTML_ALL) {
      const html = fs.readFileSync(path.join(DOCS, rel), "utf8");
      // Bir stil dosyası; ikincisi yalnız betik kapalıyken yüklenir (noscript içinde).
      const noscript = (html.match(/<noscript>[\s\S]*?<\/noscript>/g) || []).join("");
      expect.soft((html.replace(/<noscript>[\s\S]*?<\/noscript>/g, "").match(/<link rel="stylesheet"/g) || []).length, `${rel}: stil dosyası`).toBe(1);
      expect.soft((noscript.match(/<link rel="stylesheet" href="[^"]*assets\/noscript\.css"/g) || []).length, `${rel}: betiksiz stil dosyası`).toBe(1);
      expect.soft((html.match(/<script /g) || []).length, `${rel}: betik dosyası`).toBe(1);
      expect.soft((html.match(/<link rel="icon"/g) || []).length, `${rel}: sekme simgesi`).toBe(1);
      expect.soft(/<script>|<script(?![^>]*\ssrc=)/.test(html), `${rel}: satır içi betik`).toBe(false);
      expect.soft(/<style[\s>]/.test(html), `${rel}: satır içi stil öğesi`).toBe(false);
      expect.soft(/\son[a-z]+="/.test(html), `${rel}: satır içi olay işleyici`).toBe(false);
      expect.soft(html.includes('http-equiv="Content-Security-Policy"'), `${rel}: içerik güvenlik politikası`).toBe(true);
      expect.soft(html.includes('name="robots" content="noindex, nofollow"'), `${rel}: noindex`).toBe(true);
    }
  });

  test("Türkçe harf bozulması yok (birleşik nokta, yanlış büyük I)", async () => {
    const bad = [];
    for (const rel of HTML_ALL) {
      const text = fs.readFileSync(path.join(DOCS, rel), "utf8").replace(/<[^>]+>/g, " ");
      const m = text.match(/̇|(^|[\s>(“"'])I[çğıöşü]/m);
      if (m) bad.push(`${rel}: …${text.slice(Math.max(0, m.index - 20), m.index + 20)}…`);
    }
    expect(bad).toEqual([]);
  });

  test("her proje sayfasında \"bu nedir\" tanıtımı var", async () => {
    const eksik = ALL_PAGES.filter((r) => r.startsWith("proje/")).filter((r) => {
      const html = fs.readFileSync(path.join(DOCS, r), "utf8");
      return !/class="answer"/.test(html) || !/id="nedir"/.test(html) || !/class="steps/.test(html);
    });
    expect(eksik).toEqual([]);
  });

  test("indirilecek dosyalar yerinde ve boş değil", async ({ request }) => {
    for (const [name, magic] of [["bpclaude-secim-sablonu.xlsx", "PK"], ["bpclaude-secenekler.csv", null], ["bpclaude-model.json", "{"]]) {
      const res = await request.get(`indir/${name}`);
      expect(res.status(), name).toBe(200);
      const body = await res.body();
      expect(body.length, `${name} boyutu`).toBeGreaterThan(1000);
      if (magic) expect(body.subarray(0, magic.length).toString("latin1"), `${name} biçimi`).toBe(magic);
    }
  });
});

for (const url of KEY_PAGES) {
  test(`ağ: ${url} yalnız belge, bir stil ve bir betik yükler; konsol temiz`, async ({ page, baseURL }) => {
    const origin = new URL(baseURL).origin;
    const external = [], failed = [], consoleMsgs = [], requests = [];
    page.on("request", (r) => { requests.push(r.url()); if (!r.url().startsWith(origin)) external.push(r.url()); });
    page.on("response", (r) => { if (r.status() >= 400) failed.push(`${r.status()} ${r.url()}`); });
    page.on("console", (m) => { if (["error", "warning"].includes(m.type())) consoleMsgs.push(`${m.type()}: ${m.text()}`); });
    page.on("pageerror", (e) => consoleMsgs.push(`hata: ${e.message}`));
    await page.goto(url, { waitUntil: "networkidle" });
    expect.soft(external, "dış istek").toEqual([]);
    expect.soft(failed, "başarısız istek").toEqual([]);
    expect.soft(consoleMsgs, "konsol iletisi").toEqual([]);
    // Sekme simgesi tarayıcıya göre istenir ya da istenmez; istek kümesinden ayrı tutulur.
    const paths = requests.map((u) => new URL(u).pathname.replace(/^\/bpclaude\//, "")).filter((p) => p !== "assets/favicon.svg").sort();
    const beklenen = [url, "assets/site.css", "assets/site.js"].sort();
    expect(paths, "istek kümesi").toEqual(beklenen);
  });
}

test("404: iç içe bulunmayan adreste sayfa biçimli ve bağlantıları çalışır", async ({ page, baseURL }, info) => {
  test.skip(isPhoneProject(info.project.name), "not_applicable: tek profil yeterli");
  const res = await page.goto("proje/boyle-bir-sayfa-yok/derin.html");
  expect(res.status()).toBe(404);
  await expect(page.locator("h1")).toHaveText("Bu sayfa yok");
  expect(await page.evaluate(() => getComputedStyle(document.body).fontFamily)).toContain("apple-system");
  await page.locator("a.btn", { hasText: "Özete dön" }).click();
  await expect(page).toHaveURL(new URL("index.html", baseURL).href);
});

test("içerik güvenlik politikası satır içi betiği ve stil öğesini engelliyor", async ({ page }, info) => {
  test.skip(info.project.name !== "chromium", "not_applicable: tek projede yeterli");
  await page.goto("index.html");
  const r = await page.evaluate(() => {
    const s = document.createElement("script"); s.textContent = "window.__inline = true"; document.head.appendChild(s);
    const st = document.createElement("style"); st.textContent = "body{outline:7px solid red}"; document.head.appendChild(st);
    return { script: window.__inline === true, style: getComputedStyle(document.body).outlineWidth };
  });
  expect(r.script, "satır içi betik çalışmamalı").toBe(false);
  expect(r.style, "satır içi stil öğesi uygulanmamalı").not.toBe("7px");
});

test("yerel sunucu docs dışına çıkmıyor ve yabancı ana makine adını reddediyor", async ({ request, baseURL }, info) => {
  test.skip(info.project.name !== "chromium" || !/127\.0\.0\.1|localhost/.test(baseURL), "not_applicable: yalnız yerel sunucuda");
  for (const p of ["/bpclaude//etc/hosts", "/bpclaude/%2Fetc%2Fhosts", "/bpclaude/..%2F..%2F..%2Fetc%2Fhosts"]) {
    const res = await request.get(new URL(p, baseURL).href.replace("/bpclaude/%252F", "/bpclaude/%2F"));
    expect.soft(res.status(), p).toBe(404);
    expect.soft((await res.text()).includes("localhost"), `${p}: sistem dosyası içeriği`).toBe(false);
  }
  const res = await request.get(baseURL, { headers: { Host: "evil.example" } });
  expect(res.status()).toBe(421);
});
