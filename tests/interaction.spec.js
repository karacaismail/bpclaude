// Etkileşim: gezinme düğmesi, atlama bağlantısı, görünür klavye odağı, süzme ve sıralama, yön değişimi, betiksiz temel deneyim.
import { test, expect } from "@playwright/test";
import { KEY_PAGES, isPhoneProject } from "./helpers.js";

// macOS WebKit'te Tab yalnız form kontrollerinde durur; bağlantılar Option+Tab ile gezilir.
const tabKey = (browserName) => (browserName === "webkit" ? "Alt+Tab" : "Tab");

async function focusInfo(page) {
  return page.evaluate(() => {
    const el = document.activeElement;
    if (!el || el === document.body) return null;
    const cs = getComputedStyle(el);
    const ring = getComputedStyle(document.documentElement).getPropertyValue("--c-focus").trim();
    const probe = document.createElement("span");
    probe.style.color = ring;
    document.body.appendChild(probe);
    const ringRgb = getComputedStyle(probe).color;
    probe.remove();
    const parents = [];
    for (let p = el.parentElement; p; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (s.outlineStyle !== "none" && parseFloat(s.outlineWidth) > 0) parents.push(p.tagName.toLowerCase() + "." + p.className);
    }
    const r = el.getBoundingClientRect();
    return {
      etiket: el.tagName.toLowerCase() + "." + el.className, metin: el.textContent.trim().slice(0, 40),
      outlineStyle: cs.outlineStyle, outlineWidth: parseFloat(cs.outlineWidth), outlineColor: cs.outlineColor, ringRgb,
      boxShadow: cs.boxShadow, cerceveliUst: parents, gorunur: r.width > 0 && r.height > 0, ekranda: r.bottom > 0 && r.top < innerHeight,
    };
  });
}

test.describe("gezinme düğmesi (dar ekran)", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("index.html");
  });

  test("düğme menüyü açar, kapatır ve durumunu bildirir", async ({ page }) => {
    const toggle = page.locator(".nav-toggle");
    const list = page.locator("#site-nav-list");
    await expect(toggle).toBeVisible();
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await expect(list).toBeHidden();
    await toggle.click();
    await expect(toggle).toHaveAttribute("aria-expanded", "true");
    await expect(list).toBeVisible();
    await expect(list.locator("a")).toHaveCount(9);
    await toggle.click();
    await expect(list).toBeHidden();
  });

  test("klavye: Enter açar, Escape kapatır ve odağı düğmeye döndürür", async ({ page, browserName }, info) => {
    test.skip(isPhoneProject(info.project.name), "klavye denetimi masaüstü motorlarında yapılır");
    const toggle = page.locator(".nav-toggle");
    await toggle.focus();
    await page.keyboard.press("Enter");
    await expect(toggle).toHaveAttribute("aria-expanded", "true");
    await page.keyboard.press(tabKey(browserName));
    await expect(page.locator("#site-nav-list a").first()).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(toggle).toHaveAttribute("aria-expanded", "false");
    await expect(toggle).toBeFocused();
    await expect(page.locator("#site-nav-list")).toBeHidden();
  });

  test("geçerli sayfa gezinmede işaretli", async ({ page }) => {
    await page.locator(".nav-toggle").click();
    await expect(page.locator('#site-nav-list a[aria-current="page"]')).toHaveText("Özet");
    await page.locator("#site-nav-list a", { hasText: "Sıralama" }).click();
    await expect(page).toHaveURL(/siralama\.html/);
    await page.locator(".nav-toggle").click();
    await expect(page.locator('#site-nav-list a[aria-current="page"]')).toHaveText("Sıralama");
  });
});

test("geniş ekranda gezinme hep açık, düğme gizli", async ({ page }, info) => {
  test.skip(isPhoneProject(info.project.name), "geniş ekran denetimi masaüstü motorlarında yapılır");
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("index.html");
  await expect(page.locator(".nav-toggle")).toBeHidden();
  await expect(page.locator("#site-nav-list")).toBeVisible();
});

test.describe("klavye ve odak", () => {
  test.beforeEach(async ({}, info) => {
    test.skip(isPhoneProject(info.project.name), "klavye denetimi masaüstü motorlarında yapılır");
  });

  test("atlama bağlantısı ilk durak; etkinleşince sonraki durak ana içeriğin içinde", async ({ page, browserName }) => {
    await page.goto("siralama.html");
    await page.keyboard.press(tabKey(browserName));
    const skip = page.locator(".skip-link");
    await expect(skip).toBeFocused();
    await expect(skip).toBeInViewport();
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(/#icerik$/);
    await page.keyboard.press(tabKey(browserName));
    const inMain = await page.evaluate(() => !!document.activeElement && !!document.activeElement.closest("main"));
    expect(inMain, "atlama bağlantısından sonraki durak ana içerikte").toBe(true);
  });

  for (const url of KEY_PAGES) {
    test(`odak göstergesi: ${url} üzerinde her durakta tek ve görünür`, async ({ page, browserName }) => {
      await page.goto(url);
      const seen = [];
      for (let i = 0; i < 28; i++) {
        await page.keyboard.press(tabKey(browserName));
        const f = await focusInfo(page);
        if (!f) continue;
        seen.push(f.etiket);
        expect.soft(f.outlineStyle, `${url} durak ${i} ${f.etiket}: çerçeve türü`).toBe("solid");
        expect.soft(f.outlineWidth, `${url} durak ${i} ${f.etiket}: çerçeve kalınlığı`).toBeGreaterThanOrEqual(3);
        expect.soft(f.outlineColor, `${url} durak ${i} ${f.etiket}: çerçeve rengi token`).toBe(f.ringRgb);
        expect.soft(f.boxShadow, `${url} durak ${i} ${f.etiket}: ek gölge çerçevesi yok`).toBe("none");
        expect.soft(f.cerceveliUst, `${url} durak ${i} ${f.etiket}: üst kapsayıcıda çerçeve yok`).toEqual([]);
        expect.soft(f.gorunur, `${url} durak ${i} ${f.etiket}: odaklanan öğe görünür`).toBe(true);
      }
      expect(seen.length, `${url}: klavye durağı sayısı`).toBeGreaterThan(5);
    });
  }

  test("Shift+Tab geri gider", async ({ page, browserName }) => {
    await page.goto("index.html");
    const key = tabKey(browserName);
    await page.keyboard.press(key);
    await page.keyboard.press(key);
    await page.keyboard.press(key);
    const third = await focusInfo(page);
    await page.keyboard.press(key);
    await page.keyboard.press(browserName === "webkit" ? "Alt+Shift+Tab" : "Shift+Tab");
    const back = await focusInfo(page);
    expect(back.etiket + back.metin).toBe(third.etiket + third.metin);
  });

  test("açılır bölüm klavyeyle açılır ve kapanır", async ({ page }) => {
    await page.goto("sablon.html");
    const first = page.locator("#kapilar details").first();
    const summary = first.locator("summary");
    await summary.focus();
    await expect(first).not.toHaveAttribute("open", "");
    await page.keyboard.press("Enter");
    await expect(first).toHaveAttribute("open", "");
    await expect(first.locator(".details__body")).toBeVisible();
    await page.keyboard.press("Space");
    await expect(first).not.toHaveAttribute("open", "");
  });

  test("fare tıklaması odak çerçevesi bırakmıyor, klavye bırakıyor", async ({ page, browserName }) => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("siralama.html");
    const chip = page.locator('.chip[data-sort="puan"]');
    await chip.click();
    const afterClick = await chip.evaluate((el) => getComputedStyle(el).outlineStyle);
    expect(afterClick, "fareyle tıklanan düğmede çerçeve yok").toBe("none");
    await page.keyboard.press(tabKey(browserName));
    const f = await focusInfo(page);
    expect(f.outlineStyle).toBe("solid");
  });
});

test.describe("sıralama sayfası: süzme, arama, sıralama", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("siralama.html");
  });

  const visibleRows = (page) => page.locator("#liste > li:not([hidden])");

  async function openPanel(page) {
    const panel = page.locator("#suzgec-panel");
    if (!(await panel.evaluate((el) => el.open))) await panel.locator("summary").click();
  }

  test("karar süzgeci listeyi daraltır, sayaç ve düğme durumu güncellenir", async ({ page }) => {
    await openPanel(page);
    const total = await page.locator("#liste > li").count();
    await expect(page.locator("#sonuc")).toHaveText(`${total} seçenek gösteriliyor`);
    const chip = page.locator('.chip[data-filter="karar"]:not([data-value=""])').first();
    const value = await chip.getAttribute("data-value");
    await chip.click();
    await expect(chip).toHaveAttribute("aria-pressed", "true");
    await expect(page.locator('.chip[data-filter="karar"][data-value=""]')).toHaveAttribute("aria-pressed", "false");
    const n = await visibleRows(page).count();
    expect(n).toBeGreaterThan(0);
    expect(n).toBeLessThan(total);
    await expect(page.locator("#sonuc")).toHaveText(`${n} seçenek gösteriliyor`);
    const kinds = await visibleRows(page).evaluateAll((els) => [...new Set(els.map((x) => x.dataset.karar))]);
    expect(kinds).toEqual([value]);
  });

  test("nakit süzgeci karar süzgeciyle birlikte çalışır ve özet satırı güncellenir", async ({ page }) => {
    await openPanel(page);
    const chip = page.locator('.chip[data-filter="nsinif"]:not([data-value=""])').last();
    const value = await chip.getAttribute("data-value");
    await chip.click();
    const classes = await visibleRows(page).evaluateAll((els) => [...new Set(els.map((x) => x.dataset.nsinif))]);
    expect(classes).toEqual([value]);
    await expect(page.locator("#suzgec-ozet")).toContainText((await chip.textContent()).toLocaleLowerCase("tr"));
    const karar = page.locator('.chip[data-filter="karar"][data-value="degistir"]');
    await karar.click();
    const pairs = await visibleRows(page).evaluateAll((els) => [...new Set(els.map((x) => x.dataset.karar + "|" + x.dataset.nsinif))]);
    expect(pairs).toEqual([`degistir|${value}`]);
    await page.locator('.chip[data-filter="nsinif"][data-value=""]').click();
    await page.locator('.chip[data-filter="karar"][data-value=""]').click();
    await expect(page.locator("#suzgec-ozet")).toHaveText("tümü · yatırım sırası");
  });

  test("sıralama düğmeleri listeyi yeniden dizer", async ({ page }) => {
    await openPanel(page);
    await page.locator('.chip[data-sort="nakit"]').click();
    const nakit = await visibleRows(page).evaluateAll((els) => els.map((x) => parseFloat(x.dataset.nakit)));
    expect(nakit).toEqual([...nakit].sort((a, b) => b - a));
    await page.locator('.chip[data-sort="sure"]').click();
    const sure = await visibleRows(page).evaluateAll((els) => els.map((x) => parseFloat(x.dataset.sure)));
    expect(sure).toEqual([...sure].sort((a, b) => a - b));
    await page.locator('.chip[data-sort="yatirim"]').click();
    const sira = await visibleRows(page).evaluateAll((els) => els.map((x) => parseFloat(x.dataset.yatirim)));
    expect(sira).toEqual([...sira].sort((a, b) => a - b));
  });

  test("arama Türkçe harflere duyarsız: büyük, küçük ve noktalı biçimler aynı sonucu verir", async ({ page }) => {
    const q = page.locator("#q");
    const counts = [];
    for (const term of ["danışmanlık", "DANIŞMANLIK", "danismanlik", "Danişmanlik"]) {
      await q.fill(term);
      counts.push(await visibleRows(page).count());
    }
    expect(counts[0]).toBeGreaterThan(0);
    expect(new Set(counts).size, `sonuç sayıları: ${counts.join(", ")}`).toBe(1);
  });

  test("eşleşme yoksa boş durum görünür ve süzgeçler temizlenebilir", async ({ page }) => {
    const total = await page.locator("#liste > li").count();
    await page.locator("#q").fill("zzzzqqqq-yok");
    await expect(page.locator("#sonuc")).toHaveText("0 seçenek gösteriliyor");
    await expect(page.locator("#bos")).toBeVisible();
    await page.locator("#temizle").click();
    await expect(page.locator("#bos")).toBeHidden();
    await expect(visibleRows(page)).toHaveCount(total);
    await expect(page.locator("#q")).toBeFocused();
  });

  test("klavye: düğme Enter ve boşlukla çalışır", async ({ page }, info) => {
    test.skip(isPhoneProject(info.project.name), "klavye denetimi masaüstü motorlarında yapılır");
    await openPanel(page);
    const chip = page.locator('.chip[data-sort="puan"]');
    await chip.focus();
    await page.keyboard.press("Enter");
    await expect(chip).toHaveAttribute("aria-pressed", "true");
    const other = page.locator('.chip[data-sort="ogrenme"]');
    await other.focus();
    await page.keyboard.press("Space");
    await expect(other).toHaveAttribute("aria-pressed", "true");
    await expect(chip).toHaveAttribute("aria-pressed", "false");
  });

  test("seçim adreste saklanır ve sayfa yenilenince korunur; arama metni adrese yazılmaz", async ({ page }) => {
    await openPanel(page);
    const chip = page.locator('.chip[data-filter="karar"]:not([data-value=""])').first();
    const value = await chip.getAttribute("data-value");
    await chip.click();
    await page.locator('.chip[data-sort="puan"]').click();
    await page.locator("#q").fill("hizmet");
    await expect(page).toHaveURL(new RegExp(`karar=${value}`));
    await expect(page).toHaveURL(/sirala=puan/);
    expect(page.url()).not.toContain("hizmet");
    await page.reload();
    await expect(page.locator(`.chip[data-filter="karar"][data-value="${value}"]`)).toHaveAttribute("aria-pressed", "true");
    await expect(page.locator('.chip[data-sort="puan"]')).toHaveAttribute("aria-pressed", "true");
    const kinds = await visibleRows(page).evaluateAll((els) => [...new Set(els.map((x) => x.dataset.karar))]);
    expect(kinds).toEqual([value]);
  });

  test("yön değişimi: yazılan arama, açık panel ve odak korunur", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("siralama.html");
    await openPanel(page);
    const q = page.locator("#q");
    await q.fill("hizmet");
    const n = await visibleRows(page).count();
    await page.setViewportSize({ width: 844, height: 390 });
    await expect(q).toHaveValue("hizmet");
    await expect(q).toBeFocused();
    expect(await page.locator("#suzgec-panel").evaluate((el) => el.open)).toBe(true);
    await expect(visibleRows(page)).toHaveCount(n);
    await page.setViewportSize({ width: 390, height: 844 });
    await expect(q).toHaveValue("hizmet");
    await expect(visibleRows(page)).toHaveCount(n);
  });

  test("seçenek başlığı proje sayfasındaki ilgili bölüme götürür", async ({ page }) => {
    const link = visibleRows(page).first().locator(".opt__title a");
    const href = await link.getAttribute("href");
    await link.click();
    await expect(page).toHaveURL(new RegExp(href.replace(/[.#]/g, "\\$&") + "$"));
    const id = href.split("#")[1];
    await expect(page.locator(`[id="${id}"]`)).toBeInViewport();
  });
});

test.describe("dokunma", () => {
  test("dokunarak süzme ve menü çalışır", async ({ page }, info) => {
    test.skip(!isPhoneProject(info.project.name), "yalnız dokunmatik telefon profilleri");
    await page.goto("siralama.html");
    await page.locator(".nav-toggle").tap();
    await expect(page.locator("#site-nav-list")).toBeVisible();
    await page.locator(".nav-toggle").tap();
    await page.locator("#suzgec-panel > summary").tap();
    const chip = page.locator('.chip[data-filter="karar"]:not([data-value=""])').first();
    await chip.tap();
    await expect(chip).toHaveAttribute("aria-pressed", "true");
    const kinds = await page.locator("#liste > li:not([hidden])").evaluateAll((els) => [...new Set(els.map((x) => x.dataset.karar))]);
    expect(kinds.length).toBe(1);
  });

  test("hover gerektiren eylem yok: bütün bağlantı ve düğmeler dokunmayla erişilebilir", async ({ page }, info) => {
    test.skip(!isPhoneProject(info.project.name), "yalnız dokunmatik telefon profilleri");
    await page.goto("index.html");
    const hidden = await page.evaluate(() => [...document.querySelectorAll("main a, main button")].filter((el) => {
      const cs = getComputedStyle(el);
      return cs.visibility === "hidden" || cs.opacity === "0";
    }).length);
    expect(hidden).toBe(0);
  });
});

test.describe("betiksiz temel deneyim", () => {
  test.use({ javaScriptEnabled: false });

  test("betik kapalıyken içerik, gezinme ve liste kullanılabilir", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("siralama.html");
    await expect(page.locator("#site-nav-list")).toBeVisible();
    await expect(page.locator(".nav-toggle")).toBeHidden();
    await expect(page.locator("#suzgec")).toBeHidden();
    const rows = page.locator("#liste > li");
    expect(await rows.count()).toBeGreaterThan(50);
    await expect(rows.first()).toBeVisible();
    await rows.first().locator(".opt__title a").click();
    await expect(page.locator("h1")).toBeVisible();
    await expect(page).toHaveURL(/proje\//);
  });

  test("betik kapalıyken açılır bölümler ve kaydırma bölgeleri çalışır", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto("sablon.html");
    const first = page.locator("#kapilar details").first();
    await first.locator("summary").click();
    await expect(first.locator(".details__body")).toBeVisible();
    await page.goto("duyarlilik.html");
    await expect(page.locator(".table-wrap").first()).toHaveAttribute("tabindex", "0");
  });
});
