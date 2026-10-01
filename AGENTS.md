# bpclaude: çalışma kuralları

Bu depo, reklam vermeden altı ayda nakit getirecek projeyi seçmek için kurulmuş bir seçim şablonunu, 45 projenin 132 ticari seçenek olarak puanlamasını, formüllü Excel çalışma kitabını ve bunları sunan statik siteyi içerir. Site `docs/` klasöründen GitHub Pages ile yayımlanır.

Bu dosya, depoda çalışan herkes (insan ya da yapay zekâ ajanı) için bağlayıcıdır.

## Klasörler

| Klasör | İçerik |
|---|---|
| `model/` | Şablonun kendisi: `criteria.json` (hedef, kapılar, kriterler, ağırlık setleri, karar eşikleri), `sorular.json` (tanı soruları), `projeler.json` (proje kimlikleri ve başlıkları), `kapsam_disi.json` |
| `data/cards/` | Proje başına seçenek kartı: tanım, kapılar, finans girdileri, deney kartı |
| `data/scores/` | İki bağımsız değerlendiricinin puan ve kanıt kodları (`.A.json`, `.B.json`); ham gerekçeler depoda yoktur (`private/scores_full`) |
| `data/hakem/` | İkinci değerlendiricinin itirazları ve hakem kararları |
| `data/final/` | Kriter başına kalibre edilmiş son puan ve kanıt kodu |
| `data/teslim/` | Satış, teslim ve destek saatlerinin ayrıştırılmış hali |
| `data/tanitim/` | Her proje için "bu nedir?" sorusunun beş parçalı yanıtı: tür, kim için, hangi iş, nasıl çalışır, bugün nerede |
| `briefs/` | Puanlamada kullanılan görev tanımları ve yayın kuralları |
| `tools/` | Hesap, çalışma kitabı, site üretimi, doğrulama ve yayın taraması |
| `src/` | Stil tokenları, stiller ve tek betik dosyası |
| `docs/` | Üretilmiş site (elle düzenlenmez) |
| `tests/` | Playwright testleri ve görsel referanslar |
| `qa/` | Test kanıt raporu |
| `private/` | Depoya girmez. Kaynak dosya eşlemesi, yasaklı ad listesi, değerlendiricilerin ham gerekçeleri ve yayın öncesi düzeltme turunun girdi ve çıktıları |

## Komutlar

Gerekenler: Python 3.9 ve üstü (`openpyxl`, `formulas`), Node 24 (`npm ci`).

| Komut | Ne yapar |
|---|---|
| `npm run build` | Hesap, çalışma kitabı, formül doğrulaması, önbellek değerleri, site ve yayın taraması |
| `npm run serve` | Siteyi `http://127.0.0.1:4173/bpclaude/` adresinde, yayındaki yol ile sunar |
| `npm run check` | Yayın taraması: depoya girecek bütün dosyalar |
| `npm run test:hizli` | Yerel hızlı kapsam: Chromium masaüstü ve dokunmatik WebKit, görsel testler hariç |
| `npm test` | Tam kapsam: beş profil, görsel karşılaştırma dahil |
| `npm run test:gorsel:guncelle` | Görsel referansları yeniden üretir (aşağıdaki kurala bakın) |
| `npm run rapor` | Son test koşusundan `qa/RAPOR.md` üretir |
| `npm run test:canli` | Yayındaki siteye karşı Chromium ve dokunmatik WebKit testleri (görsel hariç) |

`docs/` elle düzenlenmez; değişiklik `tools/`, `src/`, `model/` ya da `data/` içinde yapılır ve `npm run build` ile üretilir.

## Yayın güvenliği (MUST)

Depo ve site herkese açıktır. Git'in izlediği her dosya yayımlanmış sayılır.

- Kişi adı, müşteri, müşteri adayı, işveren, iş ortağı ve kod ya da marka sahibi üçüncü taraf adı yazılmaz; tanımla anılır. Kurallar `briefs/GIZLILIK.md` içindedir.
- Adı verilmeyen bir tarafı tanınır kılan ayrıntı (kesin şube sayısı, iç rakam, toplantı tarihi) yazılmaz.
- Yerel dosya yolu, e-posta, IP adresi, anahtar, parola ve `.env` dosyası depoya girmez.
- Çalışan sistemlerin güvenlik açığı ayrıntısı yazılmaz.
- `private/` klasörü depoya girmez. Yasaklı ad listesinin kendisi de sızıntıdır; `tools/forbidden.py` içinde yalnız genel desenler durur.
- Her commit ve yayından önce `npm run check` sıfır ihlalle bitmelidir. Özel liste yoksa tarama eksik sayılır (çıkış kodu 2).
- Yasaklı ifade taraması adları yakalar, bağlamı yakalamaz. Yeni ya da değişen kart, hakem ve gerekçe metinleri yayından önce `briefs/BRIEF_TEMIZLIK.md` kurallarıyla okunur; öneriler `tools/temizlik.py` ile denetlenip uygulanır.
- Bütün sayfalar `noindex, nofollow` taşır. `docs/robots.txt` yalnız alan adının kökünde yayımlanırsa geçerlidir; `/bpclaude/` altındaki proje sitesinde etkisi yoktur. Bunların hiçbiri gizlilik sağlamaz; adresi bilen herkes sayfayı ve indirme dosyalarını açabilir.
- Lisans seçilmedi. Depo sahibinin kararı olmadan lisans dosyası eklenmez ya da değiştirilmez.

## Arayüz kuralları (MUST)

- Renk, yazı, boşluk, köşe, çizgi ve etkileşim ölçüleri `src/styles/tokens.css` içindeki tokenlardan gelir. `base.css` ve `components.css` içinde sabit renk ya da piksel değeri yazılmaz; test bunu denetler. Satır içi stil yalnız grafik genişlik değişkenleri içindir (puan çubuğunda `--v` ve `--p`, hunide `--w`).
- Mobil öncelik: temel kurallar 320 CSS px içindir; genişledikçe `min-width` kuralları eklenir. Kabul sırası 320, 360, 375, 390, yatay telefon, tablet, dizüstü, masaüstü.
- Kırılma noktaları: 30, 40, 48, 52, 56, 60 ve 62 rem. Yeni kırılma noktası eklenirse `tests/helpers.js` içindeki liste de güncellenir.
- Ayrım boşluk ve hizayla kurulur. Çizgi yalnız işlevsel gerekçeyle kullanılır: liste satırı, tablo satırı, form alanı, bölüm ayracı. Kart ve süs çerçevesi eklenmez.
- Odak göstergesi tektir: `:focus-visible` üzerinde `--focus-ring` (3 px, zeminle en az 3:1 karşıtlık). Odak hiçbir yerde kaldırılmaz, kapsayıcıya yayılmaz, gölge ya da ikinci çerçeveyle çoğaltılmaz.
- Dokunma hedefi `--hit` tokenıdır: ince işaretçide 44, kaba işaretçide 48 CSS px. Tek başına duran her bağlantı ve kontrol bu yüksekliktedir. Metin akışındaki bağlantılar (paragraf, tanım, tablo hücresi, liste maddesi) WCAG 2.5.8 satır içi istisnasıyla kural dışıdır; istisnanın tam listesi `tests/helpers.js` içindeki `INLINE_LINK` seçicisidir.
- Tarayıcının yerel açılır menüsü kullanılmaz. Seçim gerekirse düğme grubu (`aria-pressed`) ya da erişilebilir bir liste kutusu deseni kullanılır.
- Durum yalnız renkle anlatılmaz: kapı ve karar işaretleri biçim ve metinle de ayrışır.
- Aşamalı geliştirme: betik çalışmazsa bütün içerik, gezinme ve bağlantılar kullanılabilir kalır. Hover hiçbir eylemin tek yolu değildir; içerik gizleyip gösteren hover kuralı yazılmaz.
- Dar ekran menüsü CSS ile kapalı başlar. Betiksiz durumda "Menü" bir bağlantıdır ve listeyi `:target` ile açar; betik yüklenince aynı yerde gerçek bir düğmeye dönüşür. İlk çizimde düzen kayması olmaz; test bunu yavaş ağda ölçer.
- Uzun sayfalarda bölüm gezintisi (`.toc`) yalnız yeterli yükseklikte yapışkandır; çapa hedefi `scroll-padding-top` ile gezintinin altında kalmaz.
- Proje sayfası "Bu proje nedir?" yanıtıyla açılır ve proje sözlüğü aynı yanıtı kullanır. Yeni bir proje eklenirse tanıtımı `briefs/BRIEF_TANITIM.md` kurallarıyla yazılır ve `python3 tools/validate.py tanitim` ile denetlenir.
- Site yalnız kendi kaynaklarını yükler: bir stil dosyası, bir betik, dış istek yok, satır içi betik yok. İçerik güvenlik politikası bunu tarayıcıda da zorlar.
- Koyu tema, azaltılmış hareket ve zorunlu renk kipi tokenlarla desteklenir.
- Arayüz metinlerinde emoji kullanılmaz.

## Boyut bütçesi

Ölçüm koşulu: `docs/` altındaki dosyanın `gzip -9` boyutu. Tek profil vardır; koşullu paket yoktur.

| Kaynak | Sınır |
|---|---|
| `assets/site.css` | 8 KB |
| `assets/site.js` | 4 KB |
| Sayfa başına HTML | 64 KB |
| İlk yük (HTML, stil, betik) | 80 KB |

## Test kapsamı

Profiller: `chromium`, `firefox`, `webkit` (masaüstü) ve `telefon-chromium`, `telefon-webkit` (dokunmatik emülasyon).

- Yerel: `npm run test:hizli`. Yayın öncesi: `npm test`.
- Testler yerleşimi (kabul genişlikleri, kırılma noktalarında N−1, N, N+1, yüzde 200 yazı), etkileşimi (gezinme, klavye, odak, süzme, yön değişimi, betiksiz temel deneyim), ağı (dış istek, kırık bağlantı, bütçe, 404), erişilebilirliği (axe, belge yapısı, token karşıtlığı) ve görseli kapsar.
- Emülasyon gerçek cihaz değildir. Gerçek iOS Safari, Android ve macOS Safari denetimleri `qa/RAPOR.md` içinde ayrı satırdır ve çalıştırılmadıysa `not_run` yazılır.
- Görsel karşılaştırma katıdır: piksel toleransı yoktur. Öğe görüntüleri uzatılmış görünüm alanında alınır.
- Görsel referanslar sessizce ya da topluca yenilenmez. Yenilemeden önce önce, sonra ve fark görüntüleri incelenir, gerekçe `qa/referans-degisiklikleri/README.md` içine yazılır; değişikliği yapan kişi tek onaylayıcı olmaz.
- Atlanan her testin gerekçesi `not_run:` ya da `not_applicable:` önekiyle başlar; kanıt raporu bu öneke göre sayar.
- Kanıt raporu elle yazılmaz: `npm test` ardından `npm run rapor`.

## Puanlama kuralları

- Değerlendirme birimi proje değil ticari seçenektir: proje, müşteri, iş, tetikleyici, teklif ve fiyat, kanal, ilk satılabilir kapsam.
- Kapılar telafi edilemez. Bilinmeyen koşul sıfır puan değil, testtir.
- Puan ile kanıt ayrı tutulur. Bilinmeyen puan boş bırakılır; sıfır yazılmaz, kalanlar yüze tamamlanmaz.
- C1, C2 ve D1 puanları finans girdilerinden hesaplanır; elle yazılmaz.
- Nakit hesabı puanla toplanmaz. Kurucu saati teslim emeğini içerir; baz senaryosu altı aylık kapasiteyi aşan seçenek nakit koşulunu sağlamış sayılmaz.
- Bir deney sonuçlandığında ilgili puan ve kanıt kodu güncellenir. Ağırlıklar ve eşikler yalnız hedef değiştiğinde değişir; değişiklik `model/criteria.json` içinde yapılır ve gerekçesi notta yazılır.
- Hesap ile çalışma kitabı aynı sonucu vermelidir: `tools/verify_workbook.py` sıfır farkla bitmelidir.

## Yayın yolu

Site `https://<kullanıcı>.github.io/bpclaude/` altında sunulur. Yalnız 404 sayfası mutlak yol kullanır; yol değişirse (ör. özel alan adı) `BPCLAUDE_BASE` ortam değişkeni ile derlenir.
