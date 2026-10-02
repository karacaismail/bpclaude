// Ortak yardımcılar: sayfa listesi derlenmiş docs/ klasöründen, kırılma noktaları stil dosyalarından okunur.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const DOCS = path.join(ROOT, "docs");

export const TOP_PAGES = fs.readdirSync(DOCS).filter((f) => f.endsWith(".html") && f !== "404.html").sort();
export const PROJECT_PAGES = fs.readdirSync(path.join(DOCS, "proje")).filter((f) => f.endsWith(".html")).sort().map((f) => "proje/" + f);
export const ALL_PAGES = [...TOP_PAGES, ...PROJECT_PAGES];

// Her sayfa türünden örnek: proje sayfalarından en kısa, ortanca ve en uzun olanı.
const bySize = [...PROJECT_PAGES].sort((a, b) => fs.statSync(path.join(DOCS, a)).size - fs.statSync(path.join(DOCS, b)).size);
export const SAMPLE_PROJECTS = [...new Set([bySize[0], bySize[Math.floor(bySize.length / 2)], bySize[bySize.length - 1]])];
export const KEY_PAGES = [...TOP_PAGES, ...SAMPLE_PROJECTS];

// Kabul sırası: 320 → 360 → 375 → 390 → yatay telefon → tablet → dizüstü → masaüstü → geniş ekran; kısa yükseklikler dahil.
export const VIEWPORTS = [
  { ad: "320", width: 320, height: 568 },
  { ad: "320-kisa", width: 320, height: 480 },
  { ad: "360", width: 360, height: 740 },
  { ad: "375", width: 375, height: 667 },
  { ad: "390", width: 390, height: 844 },
  { ad: "yatay-telefon", width: 844, height: 390 },
  { ad: "kisa-yatay", width: 568, height: 320 },
  { ad: "kisa-yatay-480", width: 480, height: 320 },
  { ad: "tablet", width: 768, height: 1024 },
  { ad: "tablet-yatay", width: 1024, height: 768 },
  { ad: "dizustu", width: 1280, height: 800 },
  { ad: "genis-ekran", width: 1920, height: 1080 },
];

// Kırılma noktaları elle tutulmaz: stil dosyalarındaki min-width değerlerinden (rem × 16) türetilir.
export function cssBreakpoints() {
  const css = ["tokens.css", "base.css", "components.css"].map((f) => fs.readFileSync(path.join(ROOT, "src", "styles", f), "utf8")).join("\n");
  const rem = [...css.matchAll(/min-width:\s*([\d.]+)rem/g)].map((m) => Number(m[1]));
  return [...new Set(rem)].sort((a, b) => a - b);
}
export const BREAKPOINTS = cssBreakpoints().map((r) => Math.round(r * 16));

export const isPhoneProject = (name) => name.startsWith("telefon-");
export const tabKey = (browserName) => (browserName === "webkit" ? "Alt+Tab" : "Tab");
export const shiftTabKey = (browserName) => (browserName === "webkit" ? "Alt+Shift+Tab" : "Shift+Tab");

// Kendi içinde kayan bölgeler: içerikleri bilerek görünüm alanını aşabilir.
const SCROLLERS = ".table-wrap, .figure__scroll, .toc__list, .site-nav__list";

/** Bütün açılır bölümleri açar; kapalı içerik de ölçülsün. */
export async function openAll(page) {
  await page.evaluate(() => document.querySelectorAll("details").forEach((d) => { d.open = true; }));
}

/** Yatay taşma: belge kaydırma genişliği ve kaydırma bölgesi dışındaki her öğenin kenarları. */
export async function overflowReport(page) {
  return page.evaluate((sel) => {
    const doc = document.documentElement;
    const vw = doc.clientWidth;
    const out = [];
    for (const el of document.body.querySelectorAll("*")) {
      if (el.closest(sel) && !el.matches(sel)) continue;
      if (el.closest(".visually-hidden, .skip-link, .skip-inline")) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) continue;
      if (r.right > vw + 0.5 || r.left < -0.5) {
        out.push(`${el.tagName.toLowerCase()}.${String(el.className).split(" ").join(".")} sol=${r.left.toFixed(1)} sağ=${r.right.toFixed(1)}`);
      }
      if (out.length >= 5) break;
    }
    return { scrollWidth: doc.scrollWidth, clientWidth: vw, disarida: out };
  }, SCROLLERS);
}

/** Metin içindeki bağlantı mı? (paragraf, tablo hücresi, liste maddesi gibi akış metni) — dokunma hedefi kuralının adı konmuş istisnası. */
export const INLINE_LINK = "p a, dd a, td a, th a, figcaption a, .bullets a, .prose a, .ruling a";
