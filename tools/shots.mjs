// Tasarım incelemesi için ekran görüntüleri: node tools/shots.mjs [sayfa ...]
// Her sayfa için 320, 390 ve 1280 genişlikte ilk ekranlar alınır; yatay taşma da raporlanır. Çıktı: qa/shots/
import { chromium } from "@playwright/test";
import fs from "node:fs";

const base = "http://127.0.0.1:4173/bpclaude/";
const pages = process.argv.slice(2).length ? process.argv.slice(2) : ["index.html", "siralama.html", "sablon.html"];
const sizes = [[320, 568, "320"], [390, 844, "390"], [1280, 800, "1280"]];
const screens = Number(process.env.SCREENS || 2);
fs.mkdirSync("qa/shots", { recursive: true });
const browser = await chromium.launch();
for (const [w, h, tag] of sizes) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: w < 600 ? 2 : 1, colorScheme: process.env.SCHEME || "light" });
  const page = await ctx.newPage();
  for (const p of pages) {
    await page.goto(base + p, { waitUntil: "load" });
    if (process.env.OPEN === "1") await page.evaluate(() => document.querySelectorAll("details").forEach((d) => { d.open = true; }));
    const name = p.replace(/[\/.#]/g, "_") + (process.env.SCHEME === "dark" ? "_koyu" : "");
    for (let i = 0; i < screens; i++) {
      await page.evaluate(([y]) => window.scrollTo(0, y), [i * (h - 40)]);
      await page.screenshot({ path: `qa/shots/${name}_${tag}_${i + 1}.png` });
    }
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    console.log(p, tag, "yatay taşma:", overflow);
  }
  await ctx.close();
}
await browser.close();
