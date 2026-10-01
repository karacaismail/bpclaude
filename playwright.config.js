// bpclaude test matrisi. Yerel sunucu, siteyi yayındaki gibi /bpclaude/ yolu altında sunar.
// Motorlar: Chromium, Firefox, WebKit (masaüstü) ile dokunmatik telefon profilleri (Chromium ve WebKit).
// Emülasyon gerçek cihaz değildir; gerçek iOS Safari ve Android denetimleri qa/RAPOR.md içinde ayrı satırdır.
import { defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.PORT || 4173);
// BASE_URL verilirse testler o adrese (ör. yayındaki site) karşı koşar ve yerel sunucu başlatılmaz.
const REMOTE = process.env.BASE_URL || "";
const BASE = REMOTE || `http://127.0.0.1:${PORT}/bpclaude/`;

export default defineConfig({
  testDir: "tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  timeout: 60_000,
  reporter: [["list"], ["json", { outputFile: "test-results/results.json" }]],
  snapshotPathTemplate: "tests/__snapshots__/{platform}/{projectName}/{arg}{ext}",
  // Görsel karşılaştırma katıdır (aynı makine, aynı motor sürümü): piksel toleransı yoktur; kırpılmış ya da kaymış bir satır da yakalanır.
  expect: { toHaveScreenshot: { animations: "disabled", caret: "hide" } },
  use: { baseURL: BASE, trace: "retain-on-failure", locale: "tr-TR", timezoneId: "Europe/Istanbul" },
  webServer: REMOTE ? undefined : { command: `python3 tools/serve.py ${PORT}`, url: BASE, reuseExistingServer: true, timeout: 20_000 },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } } },
    { name: "firefox", use: { ...devices["Desktop Firefox"], viewport: { width: 1280, height: 800 } } },
    { name: "webkit", use: { ...devices["Desktop Safari"], viewport: { width: 1280, height: 800 } } },
    { name: "telefon-chromium", use: { ...devices["Pixel 7"], viewport: { width: 360, height: 740 } } },
    { name: "telefon-webkit", use: { ...devices["iPhone 13"], viewport: { width: 390, height: 664 } } },
  ],
});
