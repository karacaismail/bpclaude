# Tanıtım brifi: "Bu proje nedir?" sorusunun yanıtı

Kurucu bazı projelerini unuttuğunu söylüyor: "qral nedir? Nasıl bir yazılım? Ne yazılımı?" Senin işin, verilen her proje için bu soruyu sade Türkçeyle, teknik bilmeyen birinin de anlayacağı biçimde yanıtlamak. Metin herkese açık sitede, proje sayfasının en üstünde ve proje listesinde duracak.

## Oku
1. `briefs/GIZLILIK.md` (zorunlu; metin herkese açık yayımlanacak).
2. `data/cards/<slug>.json`: projenin yayına uygun hale getirilmiş kartı. Müşteri, işveren ve üçüncü taraflar burada nasıl anılıyorsa sen de öyle an.
3. `private/tanitim/girdi/<slug>.json`: kaynak belge yolları ve gizlilik notu. Claude çalışmasının iş planında en çok yönetici özeti, "1. Problem" ve "2. Ürün" bölümlerine; GPT çalışmasının dosyalarında ürün tanımına bak. Belgeleri yalnız oku; değiştirme. Proje klasörlerine gitme, kod çalıştırma.

## Yanıtın kuruluşu
Bir proje "nedir" diye sorulduğunda yanıt beş parçadır:
1. ne tür bir şey olduğu (tarayıcı uzantısı, web uygulaması, WordPress eklentisi, hizmet paketi, masaüstü uygulaması, oyun, içerik paketi),
2. kim için olduğu,
3. hangi işi ya da sorunu çözdüğü, yani varlık nedeni,
4. nasıl çalıştığı,
5. bugün nerede durduğu.

## Alanlar
- `bir_cumle` (60-220 karakter): kalıp "<Ad>, <kim> için <ne yapan> bir <tür>." Jargon yok; kısaltmayı açıkla. Örnek: "qral, bir web sayfasının başlığını ve adresini not ya da mesaj için istenen biçimde kopyalayan ve QR kod üreten bir Chrome uzantısıdır."
- `tur` (3-60): "Chrome uzantısı", "web uygulaması (abonelikli)", "WordPress eklentisi", "hizmet paketi (danışmanlık)" gibi.
- `ad_nereden` (null ya da 5-160): adın açılımı ya da anlamı yalnız kaynakta yazıyorsa. Uydurma.
- `kim_icin` (20-220): kim kullanır, kim öder.
- `sorun` (40-320): varlık nedeni. Bugün insanlar bu işi nasıl yapıyor, neyi kaybediyor ya da neye takılıyor.
- `nasil_calisir` (3-5 madde, her biri 10-160): kullanıcının gözünden adım adım.
- `ornek` (40-260): somut bir sahne ("Bir öğretmen derste…").
- `benzerleri` (20-240): bilinen benzer ürünler kamuya açık adlarıyla ve farkı. Yoksa "Doğrudan benzeri bulunmadı; bugün bu iş … ile yapılıyor."
- `teknoloji` (20-200): düz dille nerede çalıştığı (tarayıcıda, sunucuda, telefonda), neyle yazıldığı, verinin nerede durduğu. Güvenlik açığı ayrıntısı yazma.
- `durum` (20-220): fikir mi, prototip mi, yaklaşık ne kadar hazır, canlı mı, ödeyen müşteri var mı. Kartla tutarlı olmalı.
- `para` (20-220): nasıl para kazanır (tek seferlik satış, abonelik, hizmet bedeli). Kartın birinci seçeneğiyle tutarlı olmalı.
- `ne_degil` (null ya da 5-200): sık karıştırılabilecek şey ("Bir QR kod tarayıcısı değildir").
- `etiketler` (2-6 etiket, her biri 2-24 karakter): "tarayıcı uzantısı", "not alma" gibi.

## Kurallar
- Kaynakta olmayan özellik, müşteri ya da rakam uydurma. Belgede yazmıyorsa yazma.
- Gizlilik: kişi adı, müşteri ya da işveren adı, üçüncü tarafın iç bilgisi, yerel dosya yolu, klasör ya da dosya adı, güvenlik açığı ayrıntısı ve hukuki risk itirafı yok. Kod ya da marka üçüncü tarafa aitse "üçüncü taraf bir şirkete ait" de, adını verme.
- Proje bir yazılım ürünü değil de hizmetse bunu açıkça söyle: "Bu bir yazılım ürünü değil; … hizmetidir."
- `baz-secenekler` bir proje değildir. Karşılaştırma için kullanılan taban seçeneklerini anlat; `tur` alanına "karşılaştırma tabanı" yaz.
- Kısa cümleler, üçüncü kişi ("kurucu"), "biz" dili yok. Emoji yok.

## Çıktı
`data/tanitim/<slug>.json`:
```json
{"slug": "<slug>", "bir_cumle": "…", "tur": "…", "ad_nereden": null, "kim_icin": "…", "sorun": "…",
 "nasil_calisir": ["…", "…", "…"], "ornek": "…", "benzerleri": "…", "teknoloji": "…", "durum": "…", "para": "…",
 "ne_degil": null, "etiketler": ["…", "…"]}
```
Doğrula ve GEÇTİ yazana dek düzelt:
```
python3 tools/validate.py tanitim data/tanitim/<slug>.json
```

## Dönüş
Proje başına bir satır: `<slug>: <bir_cumle>`.
