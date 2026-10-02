# Test kanıt raporu

Bu dosya `npm run rapor` ile son test koşusundan üretilir; elle düzenlenmez.

| | |
|---|---|
| Koşu zamanı (UTC) | 2026-10-02 04:15 |
| İşletim sistemi | macOS 26.5.1 (arm64) |
| Araçlar | Node v24.21.0, Playwright 1.63.0, axe-core 4.13.0, Python 3.9.6 |
| Motorlar | chromium 153.0.8010.12, firefox 155.0, webkit 26.6 |
| Komut | `npm test` (yerel sunucu `tools/serve.py`, site `/bpclaude/` yolu altında) |
| Revizyon | 177a024 (commit edilmemiş değişiklik var) |
| docs/ ve src/ içerik özeti | `d724eb226fe9ba04` (SHA-256, ilk 16 hane) |
| Toplam | 745 pass, 0 fail, 47 not_run, 163 not_applicable; süre 79 sn |

`not_run`: araç desteği olmadığı ya da bilerek sınırlandığı için o profilde çalıştırılmayan denetim (ör. zorunlu renk emülasyonu yalnız Chromium'da var). `not_applicable`: o profilde anlamı olmayan test (ör. klavye denetimi dokunmatik profilde, dosya düzeyi denetim tek profilde). Gerekçeler test dosyalarında atlama açıklaması olarak yazılıdır.

## Profil matrisi

| Profil | Motor | Görünüm alanı | Giriş | pass | fail | not_run | not_applicable |
|---|---|---|---|---:|---:|---:|---:|
| chromium | Chromium | 1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır) | fare ve klavye | 188 | 0 | 0 | 3 |
| firefox | Firefox | 1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır) | fare ve klavye | 157 | 0 | 15 | 19 |
| webkit | WebKit | 1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır) | fare ve klavye | 157 | 0 | 15 | 19 |
| telefon-chromium | Chromium, Android emülasyonu | 360 × 740 (testler 320-1024 arasında yeniden boyutlandırır) | dokunma | 116 | 0 | 14 | 61 |
| telefon-webkit | WebKit, iOS emülasyonu | 390 × 664 (testler 320-1024 arasında yeniden boyutlandırır) | dokunma | 127 | 0 | 3 | 61 |

Motor sütunundaki emülasyon, gerçek cihaz değildir: dokunma, görünüm alanı ve kullanıcı aracısı taklit edilir.

## Katmanlar

| Katman | pass | fail | not_run | not_applicable |
|---|---:|---:|---:|---:|
| Yerleşim | 339 | 0 | 3 | 33 |
| Etkileşim ve durum geçişleri | 156 | 0 | 0 | 54 |
| Ağ ve bütünlük | 71 | 0 | 0 | 34 |
| Erişilebilirlik | 104 | 0 | 40 | 26 |
| Görsel karşılaştırma | 75 | 0 | 4 | 16 |

## Ölçümler

- en büyük sayfa siralama.html 36122 B (gzip -9)
- site.css 6011 B, site.js 3385 B (gzip -9)

## Çalıştırılmayan denetimler (not_run)

- koyu tema axe denetimi iki profilde koşar: firefox (12 test)
- koyu tema axe denetimi iki profilde koşar: telefon-chromium (12 test)
- koyu tema axe denetimi iki profilde koşar: webkit (12 test)
- layout-shift ölçümü ve ağ yavaşlatma yalnız Chromium'da var: firefox (1 test)
- layout-shift ölçümü ve ağ yavaşlatma yalnız Chromium'da var: telefon-webkit (1 test)
- layout-shift ölçümü ve ağ yavaşlatma yalnız Chromium'da var: webkit (1 test)
- zorunlu renk emülasyonu yalnız Chromium'da var: firefox (2 test)
- zorunlu renk emülasyonu yalnız Chromium'da var: telefon-chromium (2 test)
- zorunlu renk emülasyonu yalnız Chromium'da var: telefon-webkit (2 test)
- zorunlu renk emülasyonu yalnız Chromium'da var: webkit (2 test)

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
| Bağımsız QA incelemesi (yalnız okuyan inceleyici) | pass | Çalıştı: 28 bulgu. Yayın öncesi gerekenlerin hepsi ve kalanların çoğu düzeltildi; testi eklenenler otomatik katmanlarda. Açık kalan: hover durumlarının görsel referansı yok. |
| Yapay zekâ ile görsel inceleme | pass | İnceleyici ve uygulayıcı referans görüntülerine baktı; grafik etiket çakışması ve kırpılmış iki referans böyle bulundu. Deterministik kanıt değildir; piksel karşılaştırmasının yerine geçmez. |
| Görsel referansların sahibi tarafından onayı | not_run | Referanslar sahibin istediği arayüz düzenlemesiyle yeniden üretildi; önce ve sonra görüntüleri qa/ux-oncesi ve qa/ux-sonrasi altında, gerekçe qa/referans-degisiklikleri altında. Sahibin incelemesi bekliyor. |
| Gerçek tarayıcı yakınlaştırması | not_run | Yüzde 200 yazı boyutu ve metin aralığı otomatik test edildi; tarayıcının sayfa yakınlaştırması ayrıca denenmedi. |
| Gerçek yazdırma çıktısı | not_run | Yazdırma ortamı Chromium emülasyonuyla otomatik test edildi; kâğıda ya da PDF'e baskı elle denetlenmedi. |
| Yayındaki adreste koşu (npm run test:canli) | pass | 2026-10-02, commit 925a5d9 yayındayken: Chromium ve dokunmatik WebKit profillerinde görsel dışı testler; 285 pass, 0 fail, 59 atlandı. GitHub Pages 404 sayfası, istek kümesi ve indirme dosyaları canlı adreste doğrulandı. |

## Yayın taraması

595 dosya tarandı (metin 407, çalışma kitabı 1, ikili 186); özel ad listesi yüklü (13 kural); ihlal 0.
