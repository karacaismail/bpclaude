// Ortak yardımcılar: sayfa listesi derlenmiş docs/ klasöründen okunur; test, sitenin o anki içeriğine uyar.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const DOCS = path.join(ROOT, "docs");

export const TOP_PAGES = fs.readdirSync(DOCS).filter((f) => f.endsWith(".html") && f !== "404.html").sort();
export const PROJECT_PAGES = fs.readdirSync(path.join(DOCS, "proje")).filter((f) => f.endsWith(".html")).sort().map((f) => "proje/" + f);
export const ALL_PAGES = [...TOP_PAGES, ...PROJECT_PAGES];

// Her sayfa türünden en az bir örnek: hızlı kapsam. Proje sayfalarından en uzun, en kısa ve ortanca seçilir.
const bySize = [...PROJECT_PAGES].sort((a, b) => fs.statSync(path.join(DOCS, a)).size - fs.statSync(path.join(DOCS, b)).size);
export const SAMPLE_PROJECTS = [...new Set([bySize[0], bySize[Math.floor(bySize.length / 2)], bySize[bySize.length - 1]])];
export const KEY_PAGES = [...TOP_PAGES, ...SAMPLE_PROJECTS];

// Kabul sırası: 320 → 360 → 375 → 390 → yatay telefon → tablet → dizüstü → masaüstü → geniş ekran.
export const VIEWPORTS = [
  { ad: "320", width: 320, height: 568 },
  { ad: "360", width: 360, height: 740 },
  { ad: "375", width: 375, height: 667 },
  { ad: "390", width: 390, height: 844 },
  { ad: "yatay-telefon", width: 844, height: 390 },
  { ad: "kisa-yatay", width: 568, height: 320 },
  { ad: "tablet", width: 768, height: 1024 },
  { ad: "tablet-yatay", width: 1024, height: 768 },
  { ad: "dizustu", width: 1280, height: 800 },
  { ad: "genis-ekran", width: 1920, height: 1080 },
];

// Stil dosyasındaki kırılma noktaları (rem × 16). Her biri için N−1, N, N+1 denenir.
export const BREAKPOINTS = [480, 640, 768, 832, 896, 960, 992];

export const isPhoneProject = (name) => name.startsWith("telefon-");

/** Yatay taşma: belge kaydırma genişliği ve kaydırma bölgesi dışındaki her öğenin sağ kenarı. */
export async function overflowReport(page) {
  return page.evaluate(() => {
    const doc = document.documentElement;
    const vw = doc.clientWidth;
    const out = [];
    const inScroller = (el) => el.closest(".table-wrap, .figure__scroll");
    for (const el of document.body.querySelectorAll("*")) {
      if (inScroller(el) && !el.matches(".table-wrap, .figure__scroll")) continue;
      if (el.closest(".visually-hidden, .skip-link")) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      if (r.right > vw + 0.5 || r.left < -0.5) {
        out.push(`${el.tagName.toLowerCase()}.${String(el.className).split(" ").join(".")} sol=${r.left.toFixed(1)} sağ=${r.right.toFixed(1)}`);
      }
      if (out.length >= 5) break;
    }
    return { scrollWidth: doc.scrollWidth, clientWidth: vw, disarida: out };
  });
}
