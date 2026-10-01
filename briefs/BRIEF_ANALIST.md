# Analist brifi: ticari seçenek kartı ve ilk puanlama

## Amaç
Kurucu şunu soruyor: "Hangi projem, ücretli reklam olmadan, 1-6 ayda birkaç bin dolar getirir?" Değerlendirme birimi proje değil **ticari seçenektir**: proje × müşteri × müşterinin işi × tetikleyici × teklif ve fiyat × dağıtım kanalı × ilk satılabilir kapsam. Aynı projenin en çok 3 farklı ticari seçeneği olabilir (ör. aynı kodun küçük işletmeye abonelik, ajansa paket, tek müşteriye proje olarak satılması).

Senin işin bir proje için: (1) kaynak belgeleri okuyup 1-3 ticari seçeneği tanımlamak, (2) her seçenek için kapıları, finans girdilerini ve bir sonraki deneyi yazmak, (3) her seçeneği 26 kriter ve 4 stratejik kriterde puanlamak.

## Oku (sırayla)
1. `briefs/GIZLILIK.md` (yayın güvenliği; zorunlu).
2. `briefs/KRITERLER.md` (kapılar, kriterler, 1-3-5 çapaları, kanıt ölçeği).
3. Görevde verilen kaynak belgeler: Claude çalışmasının iş planı ve derinlik dosyası (varsa plan 14-18. bölümler dahil), GPT çalışmasının ilgili strateji dosyaları. Belgeleri baştan sona oku; iki çalışmanın nerede aynı, nerede farklı düşündüğünü not et. Proje klasörlerine gitme; kaynak yalnız bu belgelerdir. Belgeleri değiştirme.

## Seçenekleri nasıl seçersin
- Planın "en gerçekçi ticari biçim" dediği biçim birinci seçenektir. GPT çalışması farklı bir ilk ürün öneriyorsa (ör. platform yerine uzmanlı rapor hizmeti) onu ayrı seçenek yap.
- 6 ay içinde tahsilat ihtimali olmayan büyük biçimi (ör. dış sermaye isteyen pazar yeri) yine de bir seçenek olarak yazabilirsin; kapılar onu eler. En az bir seçenek, kurucunun tek başına 8 hafta içinde satabileceği en küçük kapsam olsun; böyle bir kapsam yoksa bunu kapılarda söyle.
- Plan bir biçim için "sunum yapılamaz / ürün değil" diyorsa o biçimi seçenek yapma; planın önerdiği komşu biçimi (hizmet paketi, başka ürünün özelliği, şablon, kod satışı) yaz.
- Seçenek kimliği: `<slug>-a`, `<slug>-b`, `<slug>-c`.

## Finans girdileri (puandan ayrı tutulur)
6 aylık pencere, işe başlandığı gün başlar. Rakamları planın 5, 6 ve 8. bölümlerinden ve GPT dosyasındaki "ücretli paket" bölümünden türet; türetimi `dayanak` alanına yaz. Plan 12 aylık rakam veriyorsa ilk 6 ayı, kalan efor ve ilk tahsilat gecikmesini düşerek hesapla; iyimser yuvarlama yapma. Kötü senaryo 0 olabilir. Tutarlar ₺, KDV hariç. USD fiyatı 48 ₺/USD ile çevir.
- `net_fiyat_tl`: tek satışın ya da bir aylık aboneliğin net tutarı.
- `alti_ay_tahsilat_tl`: 6 ayda fiilen tahsil edilen toplam (kötü / baz / iyi).
- `alti_ay_odeme_adedi`: 6 ayda ödeme adedi (tek seferlikte satış sayısı; abonelikte abone-ay sayısı).
- `alti_ay_musteri`: 6. ay sonunda ödeyen müşteri sayısı (tek seferlikte toplam alıcı).
- `degisken_maliyet_tl`: ödeme başına değişken maliyet (ödeme komisyonu, API, uzman, baskı).
- `sabit_gider_aylik_tl`: bu seçenek için ilave aylık sabit gider (barındırma, araç, muhasebe payı).
- `baslangic_nakit_tl`: ilk tahsilata kadar harcanacak nakit (hukukçu, alan adı, hesap açılışı).
- `kalan_efor_saat`: ilk ödeme alınabilecek kapsama kalan kurucu saati (min / beklenen / max).
- `ilk_tahsilat_gun`: bugünden ilk tahsilata gün (min / max).
- `satis_basina_kurucu_saati`: bir satışı kapatmak için görüşme, demo, teklif, kurulum saati.
- `musteri_basina_aylik_destek_dk`: müşteri başına aylık destek dakikası.
- `donusum_orani`: nitelikli adaydan ödeyen müşteriye dönüşüm aralığı (kanıt yoksa varsayım olduğunu `dayanak`ta söyle).

## Puanlama
Her seçenek için 26 kriter (A1-F3) ve 4 stratejik kriter (S1-S4): `p` puan (0-5 tam sayı ya da dayanak hiç yoksa `null`), `k` kanıt kodu (0-4), `g` gerekçe (10-200 karakter; hangi belge ve bölüme dayandığını söyle). Kurallar:
- Çapaya göre puanla, projeyi sevdiğine göre değil. Kriter kriter düşün; bir kriterdeki izlenimi diğerine taşıma.
- Geçmişte harcanan emek puan getirmez; yalnız kalan efor ve kullanılabilir varlık sayılır.
- "Kod var" ödeme isteği kanıtı değildir. Ödeyen müşteri yoksa A6 en çok 3, kanıtı en çok 1 olur.
- Kurucunun gerçek kişisel ağı belgelerde yazmıyorsa B1 için kanıt 0 ya da 1'dir; belgelerde adı geçen mevcut ilişki varsa bunu gerekçede söyle (ad vermeden).
- Ters yönlü kriterlerde (B6, C2, C3, C6, F1, F2, F3) yük ya da risk azaldıkça puan artar.

## Çıktı (iki dosya; uzun yazma çağrısından kaçın)
1. `data/cards/<slug>.json` — kart. Alanlar ve sınırlar aşağıda. Önce iskeleti ve ilk seçeneği yaz, sonra diğer seçenekleri ekle (dosyayı Python ile okuyup `secenekler` listesine ekleyerek); tek çağrıda 150 satırdan uzun metin yazma.
2. `data/scores/<slug>.A.json` — puanlar: `{"slug": "<slug>", "degerlendirici": "A", "puanlar": {"<seçenek kimliği>": {"A1": {"p": 3, "k": 1, "g": "…"}, …}}}`.

Doğrula ve hata kalmayana dek düzelt (çalışma klasörü deponun kökü):
```
python3 tools/validate.py kart data/cards/<slug>.json
python3 tools/validate.py puan data/scores/<slug>.A.json
```

### Kart alanları
```json
{
  "slug": "<slug>",
  "baslik": "<görevde verilen başlık, aynen>",
  "ozet": "60-420 karakter: ne, kime, bugün ne durumda",
  "bugun": {"var": ["en çok 6 madde, her biri ≤ 140"], "yok": ["en çok 6 madde"], "odeyen_musteri": 0},
  "iki_calisma": {"claude": "≤ 320: Claude planı ne diyor", "gpt": "≤ 320: GPT stratejisi ne diyor", "ayrisma": "≤ 320: nerede ayrışıyorlar", "birlesik": "≤ 320: ikisinden çıkan ortak hüküm"},
  "analist_gorusu": "≤ 280: bu proje için en gerçekçi yol ve neden",
  "secenekler": [{
    "id": "<slug>-a", "ad": "≤ 70", "tur": "yazılım ürünü | hizmet | içerik | eklenti | kod satışı | diğer",
    "musteri": "≤ 160", "is": "≤ 200", "tetikleyici": "≤ 160", "teklif": "≤ 200", "fiyat": "≤ 120",
    "kanal_birincil": "≤ 160, adıyla", "kanal_yedek": "≤ 160", "ilk_adim": "≤ 160", "ilk_kapsam": "≤ 240",
    "kapilar": {"G1": {"durum": "gecti | test | kaldi", "not": "≤ 160"}, "G2": {}, "G3": {}, "G4": {}, "G5": {}, "G6": {}, "G7": {}, "G8": {}},
    "kapi_duzeltme": "≤ 200: test ya da kaldı olanlar nasıl geçer; hepsi geçtiyse boş metin",
    "finans": {"satis_tipi": "tek seferlik | aylık abonelik | yıllık peşin | proje | karma", "net_fiyat_tl": 0, "degisken_maliyet_tl": 0, "sabit_gider_aylik_tl": 0, "baslangic_nakit_tl": 0,
      "kalan_efor_saat": {"min": 0, "beklenen": 0, "max": 0}, "ilk_tahsilat_gun": {"min": 0, "max": 0}, "satis_basina_kurucu_saati": 0, "musteri_basina_aylik_destek_dk": 0,
      "alti_ay_tahsilat_tl": {"kotu": 0, "baz": 0, "iyi": 0}, "alti_ay_odeme_adedi": {"kotu": 0, "baz": 0, "iyi": 0}, "alti_ay_musteri": {"kotu": 0, "baz": 0, "iyi": 0},
      "donusum_orani": {"dusuk": 0.01, "yuksek": 0.05}, "dayanak": "40-400 karakter"},
    "deney": {"varsayim": "≤ 200: en riskli varsayım", "yontem": "≤ 240", "sure_gun": 14, "maliyet_saat": 10, "maliyet_tl": 0, "basari_olcutu": "≤ 160", "birakma_olcutu": "≤ 160", "sonraki_dilim": "≤ 160"},
    "etiketler": {"segment": "≤ 60", "kanal_turu": "kurucu satışı | ortak | arama | pazar yeri | topluluk | içerik | ürün içi | mevcut müşteri", "teknoloji": "≤ 60", "regulasyon": "yok | KVKK | mevzuata bağlı | lisans"},
    "kanit_notlari": "80-600 karakter: puanlamaya dayanak gerçekler; belge ve bölüm adıyla"
  }]
}
```
Kapı notlarında neden o durumu verdiğini yaz. Ödeme altyapısı Türkiye'den satışta sanal POS ya da havale ile, yurt dışına satışta yasal satıcı (MoR) hizmetiyle kurulabilir; hesap açılmamışsa G3 "test"tir.

## Dönüş
Düz metin, 5-7 satır: yazdığın iki dosya, seçenek adları, kapı sonuçları (kaç geçti/test/kaldı), en yüksek ve en düşük puanlı üç kriter, iki çalışmanın ayrıştığı nokta, doğrulama sonucu.
