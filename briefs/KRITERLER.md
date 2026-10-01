# Puanlama modeli: kapılar, kriterler, ölçekler

Hedef: Ücretli reklam olmadan, ilk 6 ayda tahsil edilmiş net nakit; 3000 USD, 6 ay, kur 48 ₺/USD (varsayım). Haftalık kurucu saati 20; eşik saat ücreti 750 ₺; riske edilen nakit tavanı 50000 ₺.

## Puan ölçeği (her kriter 0-5 tam sayı)

- 0: Kriterin tersine güçlü durum
- 1: Çok zayıf
- 2: Zayıf ama mümkün
- 3: Kabul edilebilir
- 4: Güçlü
- 5: Çok güçlü

1, 3 ve 5 için kritere özel çapalar aşağıdadır; 2 ve 4 ara değerlerdir; 0 yalnız durum kriterin tam tersiyse verilir. Hiçbir dayanak yoksa puan `null` (bilinmiyor) yazılır; bilinmeyene ortalama puan verilmez.

## Kanıt ölçeği (her puanın yanında)

- 0 (E0): Yalnız varsayım ya da kurucu görüşü
- 1 (E1): Dış kaynak, masa başı araştırma ya da alıcı beyanı
- 2 (E2): Gerçek davranış sinyali: kayıt, kullanım, demo talebi, yazılı niyet
- 3 (E3): Parasal davranış: ödeme, ön ödeme, ücretli pilot, imzalı sözleşme
- 4 (E4): Birbirinden bağımsız birden çok müşteride tekrarlanan ödeme

Puan ne kadar iyi göründüğünü, kanıt bunu ne kadar bildiğimizi söyler; ikisi ayrı tutulur. Hiçbir projede ödeyen müşteri yoksa A6 için kanıt 3 ya da 4 olamaz.

## Kapılar (telafi edilemez; gecti / test / kaldi)

### G1 Haklar
Soru: Satılacak şeyin fikri mülkiyeti, lisansı, verisi ve kullandığı servislerin hakları kurucuda mı?
- gecti: Kod, içerik, marka ve veri kurucuya ait; bağımlılık lisansları satışa uygun.
- test: Hak sahipliği ya da lisans uyumu doğrulanmadı.
- kaldi: Kod ya da marka üçüncü tarafa ait ve yazılı izin yok; ya da lisans satışı engelliyor.

### G2 Hukuk ve uyum
Soru: Satış için lisans, kişisel veri ya da mevzuat engeli var mı; 6 ay içinde çözülebilir mi?
- gecti: Engel yok ya da gereken metinler ve kayıtlar hazır.
- test: Hukukçu ya da mali müşavir teyidi bekleyen konu var.
- kaldi: Faaliyet hukuka ya da platform kurallarına aykırı; ya da uyum yükü 6 aya sığmıyor.

### G3 Tahsilat yolu
Soru: Hedef alıcıdan ödeme alıp Türkiye'de yasal olarak tahsil etmenin yolu hazır mı?
- gecti: Sanal POS, havale ve fatura düzeni ya da küresel satışta yasal satıcı (MoR) hesabı hazır.
- test: Yol belli ama hesap açılmadı, test ödemesi yapılmadı.
- kaldi: Hedef pazardan ödeme almanın uygulanabilir yolu yok.

### G4 Ödeyecek alıcı
Soru: Ödeme yapacak kişi ya da şirket tipi belli mi; kurucu en az 20 hedef alıcıyı ismen sayabiliyor mu?
- gecti: Alıcı tipi net; isim listesi var ya da mevcut ilişki belgelenmiş.
- test: Alıcı tipi belli ama isim listesi yok.
- kaldi: Kimin ödeyeceği belli değil.

### G5 Reklamsız kanal
Soru: En az bir somut reklamsız kanal adıyla ve ilk adımıyla tanımlı mı?
- gecti: Birincil kanal ve ilk adım adlı; yedek kanal var.
- test: Kanal fikri var ama somut hedef (grup, dizin, ortak) adlandırılmadı.
- kaldi: Alıcının ürünü nasıl bulacağı tanımsız.

### G6 Süre
Soru: İlk satılabilir kapsama kalan kurucu eforu en çok 8 hafta mı ve satın alma döngüsü 6 aya sığıyor mu?
- gecti: Kalan efor 8 haftanın altında ve ilk tahsilat 6 ay içinde gerçekçi.
- test: Kalan efor tahmini belirsiz ya da satış döngüsü ölçülmedi.
- kaldi: Satılabilir kapsam 8 haftadan uzak ya da satın alma döngüsü 6 ayı aşıyor.

### G7 Riske edilen nakit
Soru: İlk tahsilata kadar harcanacak nakit, belirlenen tavanın altında mı?
- gecti: Gereken nakit tavanın altında.
- test: Nakit ihtiyacı hesaplanmadı.
- kaldi: İlk tahsilattan önce tavanı aşan nakit ya da dış sermaye gerekiyor.

### G8 Standart teslim
Soru: Her müşteri ayrı bir yazılım projesine dönüşmeden teslim edilebilir mi?
- gecti: Herkes aynı ürünü alır ya da hizmet sabit kapsamlı ve sabit fiyatlı pakettir.
- test: Kapsam sınırı yazılı değil.
- kaldi: Her satış özel geliştirme gerektiriyor.

## Kriterler

### A. Talep ve ödeme gerekçesi (ağırlık 25)
Sorun öncelikli mi; alıcının bugün ödeme yapma nedeni ve bütçe sahibi belli mi?

**A1 Sorunun şiddeti** (ağırlık 5). Sorun alıcıya bugün ne kaybettiriyor: para, ceza, iş gücü, gecikme?
- 1: Olsa iyi olur düzeyinde; kayıp gösterilemiyor.
- 3: Düzenli zaman ya da para kaybı var ama iş durmuyor.
- 5: Ceza, gelir kaybı ya da işin durması söz konusu; kayıp rakamla gösterilebiliyor.
- Kanıt türü: Kayıp hesabı, mevzuat metni, alıcı belgesi

**A2 Satın alma tetikleyicisi ve aciliyet** (ağırlık 5). Alıcıya şimdi almak zorundayım dedirten olay ne?
- 1: Tetikleyici yok; bir gün kullanırım.
- 3: Tekrarlayan bir olay var ama ertelenebiliyor.
- 5: Tarihi belli zorunluluk (mevzuat, denetim, son tarih) ya da her ay tekrarlayan zorunlu iş.
- Kanıt türü: Tarihli olay, takvim, mevzuat

**A3 Farkındalık ve çözüm arama** (ağırlık 3). Alıcı sorunu zaten biliyor ve çözüm arıyor mu?
- 1: Önce sorunun varlığını öğretmek gerekiyor.
- 3: Sorunu biliyor ama etkin biçimde aramıyor.
- 5: Bugün çözüm arıyor: arama yapıyor, teklif alıyor ya da rakip kullanıyor.
- Kanıt türü: Arama verisi, rakip kullanımı, teklif talebi

**A4 Bugünkü ücretli ya da elle geçici çözüm** (ağırlık 3). Alıcı bu iş için bugün para ya da emek harcıyor mu?
- 1: Hiçbir şey yapmıyor; maliyeti yok.
- 3: Excel ya da elle çözüyor; zaman harcıyor.
- 5: Bu iş için bugün para ödüyor: danışman, yazılım ya da personel.
- Kanıt türü: Rakip fiyatı, danışmanlık ücreti, iş tanımı

**A5 Kullanıcı, alıcı ve bütçe sahibinin netliği** (ağırlık 3). Sorunu yaşayan kişi satın alma kararını kendisi verebiliyor mu?
- 1: Kullanıcı, alıcı ve bütçe sahibi ayrı ve belirsiz.
- 3: Alıcı belli ama onay zinciri var.
- 5: Sorunu yaşayan kişi kendi kararı ve kartıyla satın alabiliyor.
- Kanıt türü: Karar süreci tanımı, persona

**A6 Ödeme isteği kanıtı** (ağırlık 6). Bu fiyata ödeme yapılacağını gösteren ne var?
- 1: Yalnız kurucunun görüşü.
- 3: Görüşmelerde fiyat konuşulmuş ya da alıcının benzer işe bugün ödeme yaptığı kaynakla gösterilmiş.
- 5: Ön ödeme, imzalı pilot ya da ödeyen müşteri var.
- Kanıt türü: Ödeme kaydı, sözleşme, teklif yanıtı

### B. Reklamsız erişim ve dağıtım (ağırlık 30)
Alıcı ürünü hangi yoldan bulacak; kurucu bu yola bugün erişebiliyor mu?

**B1 İlk 20-50 alıcıya doğrudan erişim** (ağırlık 8). Kurucu ilk alıcıları ismen sayabiliyor ve onlara doğrudan ulaşabiliyor mu?
- 1: İsim yok; soğuk liste.
- 3: 20 isim sayılabiliyor; yarısı ikinci derece bağlantı.
- 5: 20'den çok isim; çoğu doğrudan tanıdık ya da mevcut müşteri.
- Kanıt türü: İsim listesi, mevcut ilişki kaydı

**B2 Yüksek niyetli keşif** (ağırlık 5). Alıcı bu çözümü arama motorunda, bir pazar yerinde ya da dizinde kendisi arıyor mu?
- 1: Alıcı bu işi aramıyor; pazar yeri yok.
- 3: Arama niyeti var ama rekabet yoğun ya da hacim bilinmiyor.
- 5: Alıcı sorunu adıyla arıyor ya da hazır bir pazar yerinde çözüm arıyor.
- Kanıt türü: Arama hacmi, pazar yeri kategorisi

**B3 Kanal ve fiyat uyumu** (ağırlık 6). Seçilen kanal bu fiyatı taşıyor mu?
- 1: Çelişiyor: ucuz ürün ve kurucu satışı ya da pahalı ürün ve yalnız arama.
- 3: Uyum makul ama sınanmadı.
- 5: Bu kanal bu fiyatla en az bir kez satış getirdi.
- Kanıt türü: Satış kaydı, benzer satış geçmişi

**B4 Ürüne gömülü dağıtım** (ağırlık 5). Ürünün kullanımı, alıcı profiline uyan yeni kişilere ürünü gösteriyor mu?
- 1: Kullanım kimseye görünmüyor.
- 3: Çıktı başkalarına gidiyor ama görenler alıcı profili değil ya da seyrek.
- 5: Her kullanım alıcı profiline uyan yeni kişilere ürünü gösteriyor: davet, paylaşılan çıktı, ürün imzası.
- Kanıt türü: Çıktı örneği, davet akışı

**B5 Segment ağ yoğunluğu ve ortak kanalı** (ağırlık 3). Alıcılar birbirini tanıyor mu; ürünü kendi müşterisine önerecek bir aracı var mı?
- 1: Alıcılar dağınık; aracı yok.
- 3: Dernek, oda ya da grup var ama erişim kurulmadı.
- 5: Yoğun bağlantılı niş ve erişilebilir ortak (mali müşavir, bayi, oda) var.
- Kanıt türü: Topluluk adı, ortak görüşmesi

**B6 Kanal bağımlılığı** (ağırlık 3). Kanalın kuralı ya da görünürlüğü değişirse satış durur mu? Bu kriter ters yönlüdür: yük ya da risk azaldıkça puan artar.
- 1: Tek platforma ya da tek ilişkiye tam bağımlı.
- 3: Bir ana kanal ve bir yedek var.
- 5: Birbirinden bağımsız birden çok kanal; kural değişikliği işi durdurmaz.
- Kanıt türü: Kanal listesi

### C. Nakde hız ve satın alma kolaylığı (ağırlık 22)
İlk tahsilat ne kadar yakın; alıcı yardım almadan anlayıp satın alabiliyor mu?

**C1 İlk tahsilata kalan süre** (ağırlık 6). Bugünden ilk paranın hesaba girmesine kadar ne kadar var?
- 1: 3 aydan uzun.
- 3: 4-8 hafta.
- 5: 2 haftadan kısa.
- Kanıt türü: Plan, kalan iş listesi

**C2 İlk satılabilir kapsama kalan kurucu eforu** (ağırlık 5). İlk ödeme alınabilecek kapsama ulaşmak için bundan sonra ne kadar emek gerekiyor? Bu kriter ters yönlüdür: yük ya da risk azaldıkça puan artar.
- 1: 8 haftadan çok.
- 3: 3-5 hafta.
- 5: 1 haftadan az ya da elle hemen sunulabilir.
- Kanıt türü: Kalan iş listesi, mevcut kod durumu

**C3 Satış döngüsü ve onay zinciri** (ağırlık 4). İlk temastan ödemeye kadar ne kadar sürer; kaç kişi onaylar? Bu kriter ters yönlüdür: yük ya da risk azaldıkça puan artar.
- 1: 3 aydan uzun; çok onaylı.
- 3: 2-6 hafta.
- 5: Tek görüşmede ya da görüşmesiz karar.
- Kanıt türü: Benzer satış geçmişi

**C4 İlk değere ulaşma süresi ve kurulum** (ağırlık 3). Alıcı ilk anlamlı sonucu ne kadar sürede görüyor?
- 1: Haftalar süren kurulum ya da entegrasyon.
- 3: 1-3 günlük kurulum.
- 5: Dakikalar ya da saatler içinde ilk sonuç.
- Kanıt türü: Kurulum adımları, demo

**C5 Kendi kendine satın alınabilirlik** (ağırlık 2). Kapsam, fiyat, deneme ve ödeme görüşme yapmadan anlaşılabiliyor mu?
- 1: Demo, teklif ve sözleşme şart.
- 3: Fiyat açık ama ödeme için görüşme gerekiyor.
- 5: Fiyat, deneme ve ödeme görüşmesiz.
- Kanıt türü: Fiyat sayfası, ödeme akışı

**C6 Geçiş, entegrasyon ve güven bariyeri** (ağırlık 2). Alıcının başlamak için sistem değiştirmesi, veri taşıması ya da güvenlik incelemesi yapması gerekiyor mu? Bu kriter ters yönlüdür: yük ya da risk azaldıkça puan artar.
- 1: Veri taşıma, entegrasyon ve güvenlik incelemesi gerekiyor.
- 3: Sınırlı veri girişi yeterli.
- 5: Mevcut işe küçük bir ek; bariyer yok.
- Kanıt türü: Kurulum gereksinimleri

### D. Gelir yoğunluğu ve devamlılık (ağırlık 8)
Hedefi kaç satış kapatır; aynı müşteri neden yeniden öder?

**D1 Gelir yoğunluğu** (ağırlık 4). 6 aylık hedefi kaç satış kapatır?
- 1: 100'den çok satış gerekir.
- 3: 10-30 satış.
- 5: 1-5 satış.
- Kanıt türü: Fiyat ve hedef hesabı

**D2 Tekrar eden ihtiyaç** (ağırlık 2). Aynı müşteri neden yeniden ödeme yapar?
- 1: Tek seferlik ihtiyaç; tekrar yok.
- 3: Yılda birkaç kez.
- 5: Aylık ya da sürekli ihtiyaç; yenileme nedeni açık.
- Kanıt türü: Kullanım sıklığı

**D3 Genişleme ve fiyatın değerle uyumu** (ağırlık 2). Müşteri büyüdükçe ya da daha çok kullandıkça gelir artıyor mu?
- 1: Tek fiyat; genişleme yok.
- 3: Üst paket var.
- 5: Fiyat kullanım, şube ya da kullanıcı sayısıyla büyüyor; değerle uyumlu.
- Kanıt türü: Fiyat yapısı

### E. Kurucu avantajı ve fark (ağırlık 7)
Kurucunun bu alıcıda ve bu sorunda dışarıdan başlayan birine göre üstünlüğü ne?

**E1 Alan bilgisi, itibar ve ilişki** (ağırlık 3). Kurucu bu alanı ve bu alıcıyı dışarıdan başlayan birinden daha iyi tanıyor mu?
- 1: Alanı tanımıyor.
- 3: Alanı tanıyor; ağı sınırlı.
- 5: Alanda uzman; itibarı ve ağı var.
- Kanıt türü: Geçmiş iş, referans

**E2 Ücretsiz, yapay zekâ, Excel ve hiçbir şey yapmama seçeneğine karşı fark** (ağırlık 4). Alıcının bugünkü en kolay seçeneğini bırakması için yeterli neden var mı?
- 1: Ücretsiz güçlü bir seçenek aynı işi görüyor.
- 3: Fark var ama alıcıya anlatmak gerekiyor.
- 5: Seçenek yok ya da belirgin biçimde yetersiz; geçiş nedeni rakamla gösterilebiliyor.
- Kanıt türü: Rakip ve ikame karşılaştırması

### F. Operasyon yükü ve risk (ağırlık 8)
Satıştan sonra iş kurucuya ne kadar bağlı kalıyor; hatanın bedeli ne?

**F1 Müşteri başına kurucu emeği** (ağırlık 4). Her yeni müşteri kurucudan ne kadar kurulum, eğitim ve destek istiyor? Bu kriter ters yönlüdür: yük ya da risk azaldıkça puan artar.
- 1: Her müşteri yoğun kurulum, eğitim ve destek istiyor.
- 3: İlk kurulum elle; sonrası az.
- 5: Self-servis; müşteri başına ayda dakikalar.
- Kanıt türü: Kurulum ve destek tahmini, pilot ölçümü

**F2 Sorumluluk riski** (ağırlık 2). Hatalı çıktı müşteriye ceza ya da zarar doğurur mu? Bu kriter ters yönlüdür: yük ya da risk azaldıkça puan artar.
- 1: Hatalı çıktı müşteriye ceza ya da ciddi zarar doğurur.
- 3: Sınırlı zarar.
- 5: Zarar riski yok.
- Kanıt türü: Hukuki okuma

**F3 Standart teslim** (ağırlık 2). Müşteriler özel istek ve istisna üretiyor mu? Bu kriter ters yönlüdür: yük ya da risk azaldıkça puan artar.
- 1: Her müşteri özel geliştirme istiyor.
- 3: Yapılandırmayla çözülüyor.
- 5: Herkes aynı ürünü kullanıyor.
- Kanıt türü: Kapsam tanımı

### S. Stratejik eksen (nakit puanıyla toplanmaz)

**S1 Pazar büyüklüğü ve büyüme**. Ulaşılabilir pazar 3 yılda anlamlı bir işi taşır mı?
- 1: Çok dar ya da duran pazar.
- 3: Orta ölçekli pazar.
- 5: Büyük ve büyüyen pazar; kaynakla gösterilmiş.

**S2 Savunulabilirlik**. Rakip ya da yapay zekâ bunu ne kadar kolay kopyalar?
- 1: Birkaç haftada kopyalanır.
- 3: Bir miktar veri ya da entegrasyon üstünlüğü var.
- 5: Tescilli veri, derin entegrasyon, mevzuat uzmanlığı ya da ağ etkisi var.

**S3 Ölçeklenebilirlik**. Gelir kurucunun saatinden bağımsız büyüyebilir mi?
- 1: Gelir kurucu saatine bağlı.
- 3: Kısmen ürünleşmiş.
- 5: Yazılım geliri; ek müşterinin maliyeti düşük.

**S4 Portföy sinerjisi ve yeniden kullanılabilir öğrenme**. Bu iş başka projelerin müşterisini, kodunu ya da kanalını besliyor mu?
- 1: Yalıtık.
- 3: Bir başka projeyle ortak müşteri ya da kod.
- 5: Birden çok projenin müşterisini, kodunu ya da kanalını besliyor.
