# Test kanıt raporu

Bu dosya `npm run rapor` ile son test koşusundan üretilir; elle düzenlenmez.

| | |
|---|---|
| Koşu zamanı (UTC) | 2026-10-01 21:33 |
| İşletim sistemi | macOS 26.5.1 (arm64) |
| Araçlar | Node v24.21.0, Playwright 1.63.0, axe-core 4.13.0, Python 3.9.6 |
| Motorlar | chromium 153.0.8010.12, firefox 155.0, webkit 26.6 |
| Komut | `npm test` (yerel sunucu `tools/serve.py`, site `/bpclaude/` yolu altında) |
| Toplam | 678 pass, 0 fail, 167 not_applicable; süre 64 sn |

`not_applicable`: o profilde anlamı olmayan test (ör. klavye denetimi dokunmatik profilde, dosya düzeyi denetim tek profilde). Atlanan testlerin gerekçesi test dosyasında yazılıdır.

## Profil matrisi

| Profil | Motor | Görünüm alanı | Giriş | pass | fail | not_applicable |
|---|---|---|---|---:|---:|---:|
| chromium | Chromium | 1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır) | fare ve klavye | 166 | 0 | 3 |
| firefox | Firefox | 1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır) | fare ve klavye | 143 | 0 | 26 |
| webkit | WebKit | 1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır) | fare ve klavye | 143 | 0 | 26 |
| telefon-chromium | Chromium, Android emülasyonu | 360 × 740 (testler 320-1024 arasında yeniden boyutlandırır) | dokunma | 107 | 0 | 62 |
| telefon-webkit | WebKit, iOS emülasyonu | 390 × 664 (testler 320-1024 arasında yeniden boyutlandırır) | dokunma | 119 | 0 | 50 |

Motor sütunundaki emülasyon, gerçek cihaz değildir: dokunma, görünüm alanı ve kullanıcı aracısı taklit edilir.

## Katmanlar

| Katman | pass | fail | not_applicable |
|---|---:|---:|---:|
| Yerleşim | 326 | 0 | 29 |
| Etkileşim ve durum geçişleri | 121 | 0 | 44 |
| Ağ ve bütünlük | 68 | 0 | 22 |
| Erişilebilirlik | 102 | 0 | 58 |
| Görsel karşılaştırma | 61 | 0 | 14 |

## Başarısız testler

Yok.

## Otomatik koşmayan katmanlar

| Katman | Durum | Not |
|---|---|---|
| Gerçek macOS Safari | not_run | WebKit motoru Playwright ile koştu; gerçek Safari sürücüsü sistem ayarı gerektirdiği için çalıştırılmadı. |
| Gerçek iOS Safari (cihaz) | not_run | Yalnız WebKit dokunmatik emülasyonu koştu. Sanal klavye ve güvenli alan gerçek cihazda denenmedi. |
| Gerçek Android Chrome (cihaz) | not_run | Yalnız Chromium dokunmatik emülasyonu koştu. |
| Ekran okuyucu ile elle denetim | not_run | VoiceOver, NVDA ya da TalkBack ile denenmedi; axe ve belge yapısı testleri otomatik koştu. |
| Zorunlu renk kipi (gerçek işletim sistemi) | not_run | Chromium emülasyonu otomatik testte; Windows yüksek karşıtlıkta denenmedi. |
| Sürekli tümleştirme (CI) | not_run | Kurulmadı; testler yalnız yerelde koştu. Yerel geçiş, CI geçişi değildir. |
| Ağ izolasyonu (koşullu paket) | not_applicable | Tek profil vardır: bir stil dosyası ve bir betik. Koşullu ya da gizlenmiş ek paket yoktur; istek sayısı testle sınırlandı. |
| Görsel referansların sahibi tarafından onayı | not_run | Referanslar ilk kez bu teslimde üretildi. Test düzeneğinden kaynaklanan iki hatalı referans düzeltildi; önce ve sonra görüntüleri gerekçesiyle qa/referans-degisiklikleri altında. Depo sahibinin incelemesi bekliyor. |

## Yayın taraması

491 dosya tarandı (metin 361, çalışma kitabı 1, ikili 128); özel ad listesi yüklü (13 kural); ihlal 0.
