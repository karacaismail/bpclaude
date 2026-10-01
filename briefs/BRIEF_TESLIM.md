# Teslim emeği brifi: satış, teslim ve destek saatlerini ayrıştır

Altı aylık nakit hesabında kurucu saati şöyle hesaplanır:

`kalan efor + müşteri sayısı × satış başına saat + ödeme adedi × (teslim saati + aylık destek dakikası ÷ 60)`

İlk turda "teslim saati" girdisi yoktu. Hizmet seçeneklerinde işin kendisini yapmak için harcanan saat ya hiç sayılmadı ya da destek dakikasına ya da satış saatine gömüldü; bu yüzden saat başı nakit olduğundan yüksek göründü. Senin işin, sana verilen projelerin her seçeneği için bu üç girdiyi ayrıştırmak.

## Oku
- `briefs/GIZLILIK.md`
- Görevde verilen her proje için `data/cards/<slug>.json`: seçenek tanımı (teklif, fiyat, ilk kapsam), `finans` girdileri ve `finans.dayanak`.

Yalnız karttaki bilgiyi kullan; kaynak belgelere gitme, web araması yapma, kartı değiştirme.

## Her seçenek için yaz
- `satis_basina_kurucu_saati`: yalnız satışı kapatma emeği (görüşme, demo, teklif, sözleşme). Karttaki değer işin teslimini ya da kurulumunu da içeriyorsa o kısmı teslim saatine taşı.
- `teslim_saat_odeme_basina`: bir ödeme karşılığında **kurucunun kendisinin** harcayacağı teslim emeği, saat. "Ödeme", karttaki `alti_ay_odeme_adedi` birimidir:
  - tek seferlik satışta: satış başına teslim saati (kurulum, uyarlama, rapor yazımı, eğitim oturumu, proje işi);
  - taksitle ödenen projede: projenin toplam teslim saati ÷ baz senaryodaki ödeme adedi;
  - aylık hizmette: müşteri başına aylık teslim saati;
  - kopyası satılan üründe (yazılım lisansı, abonelik, eklenti, e-kitap, şablon): müşteriye özel iş yoksa 0;
  - canlı eğitim ya da kohortta: toplam ders, hazırlık ve geri bildirim saati ÷ baz senaryodaki ödeme adedi.
  Değişken maliyete yazılmış taşeron ya da uzman emeği sayılmaz; yalnız kurucunun saati sayılır.
- `musteri_basina_aylik_destek_dk`: yalnız satış sonrası destek (soru, hata, küçük düzeltme), dakika. Karttaki değer aylık hizmetin kendisini içeriyorsa o kısmı teslim saatine taşı.
- `not`: 20-240 karakter. Teslim saatini neye dayandırdığını yaz (ör. "5 günlük aylık paket 40 saat; karttaki 30 dk yalnız yazışma"). Kartta dayanak yoksa "varsayım" de. Gizlilik kurallarına uy.

## Tutarlılık denetimi
- Bir iş günü 8 saattir. Fiyatı gün ya da saat üzerinden tanımlanmış hizmette teslim saati, satılan gün ya da saatten az olamaz.
- Sabit fiyatlı pakette kapsamı (sayfa sayısı, rapor, atölye, kurulum) saate çevir; iyimser olma. Yapay zekâ araçlarıyla hızlanma varsa en çok yarıya indir ve notta söyle.
- Baz senaryo toplamını hesapla: `kalan_efor_saat.beklenen + alti_ay_musteri.baz × satış + alti_ay_odeme_adedi.baz × (teslim + destek ÷ 60)`. Altı ayda kurucunun kapasitesi 520 saattir (haftada 20 saat); toplam bunu aşıyorsa rakamları değiştirme, notta "kapasiteyi aşıyor" yaz.

## Çıktı
Her proje için `data/teslim/<slug>.json`:
```json
{"slug": "<slug>", "secenekler": {"<seçenek kimliği>": {"satis_basina_kurucu_saati": 8, "teslim_saat_odeme_basina": 40, "musteri_basina_aylik_destek_dk": 30, "not": "…"}}}
```
Karttaki bütün seçenek kimlikleri yer almalı. Her dosyayı doğrula:
```
python3 tools/validate.py teslim data/teslim/<slug>.json
```

## Dönüş
Düz metin; seçenek başına bir satır: kimlik, baz senaryoda eski toplam kurucu saati → yeni toplam, teslim saati.
