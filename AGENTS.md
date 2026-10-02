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

- Renk, yazı, boşluk, köşe, çizgi ve etkileşim ölçüleri `src/styles/tokens.css` içindeki tokenlardan gelir. `base.css` ve `components.css` içinde sabit renk ya da piksel değeri yazılmaz; test bunu denetler. Satır içi stil yalnız grafik ölçü değişkenleri içindir (puan çubuğunda `--v` ve `--p`, hunide `--w`, nakit aralığında `--a`, `--w`, `--b`, `--z`, `--t`, karar dağılımında `--n`).
- Mobil öncelik: temel kurallar 320 CSS px içindir; genişledikçe `min-width` kuralları eklenir. Kabul sırası 320, 360, 375, 390, yatay telefon, tablet, dizüstü, masaüstü.
- Kırılma noktaları: 30, 40, 48, 52, 56, 60 ve 62 rem. Yeni kırılma noktası eklenirse `tests/helpers.js` içindeki liste de güncellenir.
- Ayrım boşluk ve hizayla kurulur. Çizgi yalnız işlevsel gerekçeyle kullanılır: liste satırı, tablo satırı, form alanı, bölüm ayracı. Kart ve süs çerçevesi eklenmez.
- Odak göstergesi tektir: `:focus-visible` üzerinde `--focus-width` kalınlığında, `--c-focus` renginde tek çerçeve (zeminle en az 3:1 karşıtlık; koyu kapak bandında renk kapak değerine geçer). Odak hiçbir yerde kaldırılmaz, kapsayıcıya yayılmaz, gölge ya da ikinci çerçeveyle çoğaltılmaz. Site başlığında ve kayan şeritlerde (gezinme, bölüm gezintisi) çerçeve içe çizilir: şerit kutusu ya da ekran kenarı çerçeveyi kırpmaz. Test her durakta çerçeve kutusunun kırpılmadığını ölçer.
- Dokunma hedefi `--hit` tokenıdır: ince işaretçide 44, kaba işaretçide 48 CSS px. Tek başına duran her bağlantı ve kontrol bu yüksekliktedir. Metin akışındaki bağlantılar (paragraf, tanım, tablo hücresi, liste maddesi) WCAG 2.5.8 satır içi istisnasıyla kural dışıdır; istisnanın tam listesi `tests/helpers.js` içindeki `INLINE_LINK` seçicisidir.
- Tarayıcının yerel açılır menüsü kullanılmaz. Seçim gerekirse düğme grubu (`aria-pressed`) ya da erişilebilir bir liste kutusu deseni kullanılır.
- Durum yalnız renkle anlatılmaz. Kapı işaretleri biçimle ayrışır (dolu daire geçti, yarım daire test, içi boş kare kaldı); karar etiketlerinin her birinin ayrı işareti ve yazısı vardır. Liste satırında görünür metin geçen kapı sayısını verir (ör. 4/8 geçti), tam döküm aynı öğede ekran okuyucuya açıktır; proje sayfasında tam döküm görünür yazılır.
- Aşamalı geliştirme: betik çalışmazsa bütün içerik, gezinme ve bağlantılar kullanılabilir kalır. Hover hiçbir eylemin tek yolu değildir; içerik gizleyip gösteren hover kuralı yazılmaz.
- Gezinme her genişlikte görünür ve betik gerektirmez: dar ekranda yatay kayan şerit, 60 rem ve üstünde tek satır. Açılır menü düğmesi yoktur. Betik üç şey yapar: geçerli sayfanın bağlantısını şeridin görünen kısmına getirir, şeridin konumunu (`data-kenar`: bas, orta, son) bildirir ki devamı olan kenar solsun, klavyeyle gelinen bağlantıyı (ileri ve geri yönde) solma bölgesinin dışına kaydırır. Bu kaydırma yalnız klavye odağında yapılır: fare ya da dokunmayla basılan bağlantı işaretçinin altından kaydırılırsa tıklama boşa gider. Alt bölümdeki gezinme şeritle aynı sayfaları aynı adlarla verir: şeritte kaydıramayan kullanıcının ikinci yoludur.
- Koyu kapak bandı (site başlığı, özet sayfasının başı, alt bölüm) `.on-cover` sınıfıyla kurulur. Bu sınıf renk tokenlarını kapak değerlerine çevirir; içindeki bileşenler aynı tokenları kullanır ve kendiliğinden uyar. Kapak için ayrı bileşen stili yazılmaz. Durum renkleri (geçti, test, kaldı ve karar etiketleri) kapak için çevrilmez; bu bileşenler koyu bantta kullanılmaz ve test bunu denetler. Atlama bağlantısı site başlığının ilk öğesidir.
- Veri grafikleri CSS ile çizilir ve tek motifi paylaşır: dolu çizgi kanıtı, taralı çizgi varsayımı gösterir. Puan çubuğu, eleme hunisi, karar dağılımı ve nakit aralığı çizgisi bu aileye aittir. Boş iz `--c-track` rengindedir (zeminden ayrışır). Nakit aralığı çizgisinin ölçeği doğrusaldır: sıfır yüzde 25'te, hedef yüzde 75'te durur. Baz değer artıysa nokta dolu, eksiyse içi boştur; çentikler izin üstüne ve altına eşit taşar ve noktanın arkasında kalır (nokta çentiğin üstüne gelince çentiğin iki ucu halenin dışından görünür); aralık ölçeği aşarsa o uca ok konur, baz değerin kendisi ölçek dışındaysa nokta çizilmez; noktanın yanında kırıntı kadar kalan tarama çizilmez (kural `tools/sitelib.py` içinde `RANGE_HALE` ve `RANGE_KIRINTI`). Puan çubuğu ile nakit izi aynı kalınlıktadır ve yan yana durduklarında aynı yüksekliktedir. Sayıları bitişik metinde yazan grafik yardımcı teknolojiden gizlenir (yineleme olmasın); hedef tutarı işaretler bölümünde ve proje başında metin olarak yazılır.
- Marka turuncusu vurgu rengidir: öne çıkan karar (önce test et), vurgu sayıları, bağlantılar, bölüm üst etiketleri ve hedef çentiği. Olumsuz durum için kullanılmaz: kapıda kalan seçenek kırmızı ya da turuncu değil nötr mürekkeptir ve işareti çarpıdır.
- Ölçü bileşeni (`.metric`: ad, değer, grafik, ek bilgi) liste satırında ve proje başında aynıdır. Dar ekranda ad solda, değer sağda, grafik altındadır; geniş ekranda dört ölçü aynı taban çizgisine oturur.
- Liste sayfalarında içerik ilk ekrana girer: 390×844'te ilk seçenek satırının başlığı, kararı, puanı ve nakit değeri; 1280×800'de ilk üç satırın başlığı görünür. Bunun için süzgeç paneli kapalı başlar, işaretlerin açıklaması açılır bölümde durur ve sayfa başı kısa tutulur. Geniş ekranda sayfa başındaki şekil, araç satırı ve satırlardaki ölçü sütunu aynı üç sütunlu ızgarayı kullanır; üçü de aynı dikey çizgide başlar. Ölçütler `tests/kabul.spec.js` içindedir.
- Özet sayfasında "kısa liste" başlığı altında yalnız kısa listeye giren seçenekler durur; hemen dışında kalanlar ayrı başlık altındadır. Sayı, kapaktaki huninin kısa liste sayısıyla aynıdır.
- Tablolar dar ekranda kendi bölgesinde yatay kayar: ilk sütun (satır adı) yerinde kalır, devamı olan sağ kenar solar, bölge klavyeyle odaklanınca maske kalkar. Belirleyici sütunlar addan hemen sonra gelir ki telefonda kaydırmadan görünsün; sütun başlıkları kısa tutulur ve alta hizalanır. Satır adı kısa bir kod olan tablo `tbl--kod` sınıfını alır ve kaymadan sığar. Uzun metin sütunları olan içerik tablo değil liste olarak verilir.
- Renk geçişleri yalnız üzerine gelme durumunda tanımlıdır; sayfa yüklenirken renk canlanmaz. Giriş canlandırması yalnız sayfa başındaki (kapak ve sayfa başı bandı) çubukların büyümesidir ve hareket azaltma tercihinde kapalıdır. Liste satırları canlandırılmaz; süzme ve arama satırları yerinden oynatmaz.
- Uzun sayfalarda bölüm gezintisi (`.toc`) yalnız yeterli yükseklikte yapışkandır; çapa hedefi `scroll-padding-top` ile gezintinin altında kalmaz. Betik, sayfa kaydıkça bulunulan bölümün bağlantısını işaretler (`aria-current="location"`) ve şeritte görünür tutar. Proje sayfası ile şablon aynı gezintiyi kullanır.
- Proje sayfası "Bu proje nedir?" yanıtıyla açılır ve proje sözlüğü aynı yanıtı kullanır. Yeni bir proje eklenirse tanıtımı `briefs/BRIEF_TANITIM.md` kurallarıyla yazılır ve `python3 tools/validate.py tanitim` ile denetlenir.
- Site yalnız kendi kaynaklarını yükler: bir stil dosyası, bir betik, dış istek yok, satır içi betik yok. İçerik güvenlik politikası bunu tarayıcıda da zorlar. Betik gerektiren araçlar (arama ve süzgeç formları) HTML'de yer tutar ama betik çalışana kadar görünmez (`visibility: hidden`; betik `html` öğesine `js` sınıfını ekler). Böylece betik yüklenince yerleşim kaymaz, betik yüklenemezse de işlevsiz kontrol görünmez. Betik tümüyle kapalıysa `noscript` içindeki küçük stil dosyası (`assets/noscript.css`) formları yerleşimden de çıkarır. Yayımlanan betik, kaynaktaki yorum satırları ve girinti çıkarılarak üretilir (`minify_js`, satır tabanlıdır: kaynakta çok satırlı şablon dizgisi kullanılmaz). Sekme simgesi `src/favicon.svg` dosyasıdır; renkleri kapak tokenlarıyla aynıdır ve test bunu denetler.
- Koyu tema (yalnız ekranda; kâğıda açık tema basılır), azaltılmış hareket ve zorunlu renk kipi tokenlarla desteklenir. Zorunlu renkte grafiklerin izi ile dolgusu ayrı sistem renklerine bağlanır.
- İki yazı tipi ailesi vardır: başlık ve sayılar için serif, gövde için sans. Kodlar (kriter ve kanıt kodları) gövde yazı tipiyle kalın yazılır; üçüncü bir aile eklenmez.
- Hedef tarayıcılar güncel Chromium, Firefox ve Safari'dir (testler bu üç motorda koşar). Daha eski sürümlerde kenar solması gibi süslemeler görünmeyebilir; içerik, gezinme ve işlev aynı kalır. Stil küçültücü (`minify_css`) çarpma ve bölme çevresindeki boşluğu ve baştaki sıfırı siler: stil dosyalarında boşlukla yazılmış `*` soy seçicisi ve içinde bu desenler geçen dizgi kullanılmaz.
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
- Testler yerleşimi (kabul genişlikleri, kırılma noktalarında N−1, N, N+1, yüzde 200 yazı), etkileşimi (gezinme, klavye, odak, süzme, yön değişimi, betiksiz temel deneyim), ağı (dış istek, kırık bağlantı, bütçe, 404), erişilebilirliği (axe, belge yapısı, token karşıtlığı), tasarım kabul ölçütlerini (ilk ekranda içerik, satır yüksekliği, renk ve biçim ayrımı, sayfalar arası tutarlılık) ve görseli (üzerine gelme, odak ve seçili durumlar dahil) kapsar.
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
