# Test kanıt raporu

Bu dosya `npm run rapor` ile son test koşusundan üretilir; elle düzenlenmez.

| | |
|---|---|
| Koşu zamanı (UTC) | 2026-10-02 07:54 |
| İşletim sistemi | macOS 26.5.1 (arm64) |
| Araçlar | Node v24.21.0, Playwright 1.63.0, axe-core 4.13.0, Python 3.9.6 |
| Motorlar | chromium 153.0.8010.12, firefox 155.0, webkit 26.6 |
| Komut | `npm test` (yerel sunucu `tools/serve.py`, site `/bpclaude/` yolu altında) |
| Revizyon | d362c6a |
| docs/ ve src/ içerik özeti | `0bb3317a0fb1fd5a` (SHA-256, ilk 16 hane) |
| Toplam | 953 pass, 0 fail, 51 not_run, 191 not_applicable; süre 98 sn |

`not_run`: araç desteği olmadığı ya da bilerek sınırlandığı için o profilde çalıştırılmayan denetim (ör. zorunlu renk emülasyonu yalnız Chromium'da var). `not_applicable`: o profilde anlamı olmayan test (ör. klavye denetimi dokunmatik profilde, dosya düzeyi denetim tek profilde). Gerekçeler test dosyalarında atlama açıklaması olarak yazılıdır.

## Profil matrisi

| Profil | Motor | Görünüm alanı | Giriş | pass | fail | not_run | not_applicable |
|---|---|---|---|---:|---:|---:|---:|
| chromium | Chromium | 1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır) | fare ve klavye | 236 | 0 | 0 | 3 |
| firefox | Firefox | 1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır) | fare ve klavye | 202 | 0 | 16 | 21 |
| webkit | WebKit | 1280 × 800 (testler 320-1920 arasında yeniden boyutlandırır) | fare ve klavye | 202 | 0 | 16 | 21 |
| telefon-chromium | Chromium, Android emülasyonu | 360 × 740 (testler 320-1024 arasında yeniden boyutlandırır) | dokunma | 151 | 0 | 15 | 73 |
| telefon-webkit | WebKit, iOS emülasyonu | 390 × 664 (testler 320-1024 arasında yeniden boyutlandırır) | dokunma | 162 | 0 | 4 | 73 |

Motor sütunundaki emülasyon, gerçek cihaz değildir: dokunma, görünüm alanı ve kullanıcı aracısı taklit edilir.

## Katmanlar

| Katman | pass | fail | not_run | not_applicable |
|---|---:|---:|---:|---:|
| Yerleşim | 334 | 0 | 3 | 33 |
| Etkileşim ve durum geçişleri | 174 | 0 | 0 | 56 |
| Ağ ve bütünlük | 71 | 0 | 0 | 34 |
| Erişilebilirlik | 106 | 0 | 40 | 34 |
| Tasarım kabul ölçütleri | 171 | 0 | 4 | 10 |
| Görsel karşılaştırma | 97 | 0 | 4 | 24 |

## Ölçümler

- en büyük sayfa siralama.html 39675 B (gzip -9)
- site.css 8123 B, site.js 3505 B (gzip -9)

## Çalıştırılmayan denetimler (not_run)

- koyu tema axe denetimi iki profilde koşar: firefox (12 test)
- koyu tema axe denetimi iki profilde koşar: telefon-chromium (12 test)
- koyu tema axe denetimi iki profilde koşar: webkit (12 test)
- layout-shift ölçümü ve ağ yavaşlatma yalnız Chromium'da var: firefox (1 test)
- layout-shift ölçümü ve ağ yavaşlatma yalnız Chromium'da var: telefon-webkit (1 test)
- layout-shift ölçümü ve ağ yavaşlatma yalnız Chromium'da var: webkit (1 test)
- zorunlu renk emülasyonu yalnız Chromium'da var: firefox (3 test)
- zorunlu renk emülasyonu yalnız Chromium'da var: telefon-chromium (3 test)
- zorunlu renk emülasyonu yalnız Chromium'da var: telefon-webkit (3 test)
- zorunlu renk emülasyonu yalnız Chromium'da var: webkit (3 test)

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
| Bağımsız QA incelemesi (yalnız okuyan inceleyici) | pass | Bu düzenleme için üç tur çalıştı (yalnız okuyan kod inceleyicisi). Birinci tur: 2 yüksek, 6 orta bulgu. İkinci tur: 2 önemli bulgu (kayan şeritte fareyle ilk tıklamanın boşa gitmesi, zorunlu renkte huni çubukları) ve 12 küçük bulgu. Üçüncü tur: engelleyici bulgu yok, 1 önemli bulgu (taşan tabloda odak çerçevesinin maskede solması) ve 8 küçük bulgu. Önemli bulguların hepsi düzeltildi ve regresyon testine bağlandı; tıklama testinin düzeltme kaldırılınca başarısız olduğu ayrıca denendi. Üçüncü turdan sonraki son düzeltmeler yeniden incelenmedi; otomatik testlerle doğrulandı. Açık kalan küçükler: eski tarayıcı tabanının yazılı olmaması, sekme simgesi için PNG yedeği. |
| Yapay zekâ ile görsel inceleme | pass | Bağımsız tasarım eleştirmeni üç turda ekran görüntülerine baktı: birinci turda telefon 6,5 ve masaüstü 7, ikinci turda 7 ve 8, üçüncü turda 7,5 ve 8,5 puan verdi; son hüküm küçük düzeltmelerle yayımlanabilir. Üçüncü turun pürüzleri (tablo başlığındaki boşluk, sütun sırası, çentik ve tarama kırıntısı, sözlükte boş sütun) sonradan düzeltildi ve yeniden puanlanmadı. Deterministik kanıt değildir; piksel karşılaştırmasının yerine geçmez. |
| Görsel referansların sahibi tarafından onayı | not_run | Referanslar sahibin istediği arayüz düzenlemeleriyle yeniden üretildi; önce ve sonra görüntüleri qa/ux-oncesi, qa/ux-sonrasi, qa/ux2-oncesi ve qa/ux2-sonrasi altında, gerekçe qa/referans-degisiklikleri altında. Sahibin incelemesi bekliyor. |
| Gerçek tarayıcı yakınlaştırması | not_run | Yüzde 200 yazı boyutu ve metin aralığı otomatik test edildi; tarayıcının sayfa yakınlaştırması ayrıca denenmedi. |
| Gerçek yazdırma çıktısı | not_run | Yazdırma ortamı Chromium emülasyonuyla otomatik test edildi; kâğıda ya da PDF'e baskı elle denetlenmedi. |
| Yayındaki adreste koşu (npm run test:canli) | pass | Yayındaki siteye karşı koştu (revizyon d362c6a, 2026-10-02): Chromium masaüstü ve dokunmatik WebKit, görsel testler hariç; 360 pass, 0 fail, 68 atlandı. Yayındaki stil dosyasının özeti yerel derlemeyle aynı. Yerel sunucuya özgü testler bu koşuda atlanır. |

## Yayın taraması

696 dosya tarandı (metin 411, çalışma kitabı 1, ikili 283); özel ad listesi yüklü (13 kural); ihlal 0.
