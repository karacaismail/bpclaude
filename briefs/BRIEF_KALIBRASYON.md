# Kalibrasyon brifi: tek kriterin bütün seçenekler boyunca son puanı

Bütün ticari seçenekler iki bağımsız değerlendirici (A ve B) tarafından puanlandı. Proje proje puanlamada bir projeye duyulan genel izlenim kriterlere yayılır ve aynı durum farklı projelerde farklı puan alabilir. Senin işin **tek bir kriteri** bütün seçenekler boyunca tek elden gözden geçirip son puanı vermek: aynı gözlemlenebilir durum her seçenekte aynı puanı almalı.

## Oku
1. `briefs/GIZLILIK.md` ve `briefs/KRITERLER.md` (özellikle senin kriterinin sorusu, 1-3-5 çapaları ve kanıt ölçeği).
2. `data/calib/kartlar.md`: bütün seçeneklerin özet kartları (müşteri, iş, tetikleyici, teklif, fiyat, kanal, ilk kapsam, kapılar, finans özeti, kanıt notları).
3. `data/calib/<KRITER>.json`: her seçenek için A ve B'nin bu kriterdeki puanı (`p`), kanıt kodu (`k`) ve gerekçesi (`g`).

## Nasıl karar verirsin
- Her seçenek için kartı ve iki gerekçeyi oku; çapaya en uygun puanı ver. A ile B aynıysa ya da 1 puan farklıysa otomatik ortalama alma; hangisi çapaya uyuyorsa onu seç. 2 ve üstü fark varsa iki gerekçeyi kartla karşılaştır ve gerekçende hangisini neden seçtiğini söyle.
- Önce bütün listeyi tara, 1, 3 ve 5'e en iyi uyan birkaç seçeneği belirle; diğerlerini onlara göre yerleştir. Aynı gerçeklere sahip seçenekler aynı puanı almalı.
- Puan 0-5 tam sayıdır. Kartta ve gerekçelerde hiçbir dayanak yoksa `null` yaz; bilinmeyene ortalama puan verme.
- Kanıt kodu (0-4) puandan bağımsızdır: iddia yalnız varsayımsa 0; dış kaynak, kamuya açık fiyat ya da beyan varsa 1; kayıt, kullanım, yazılı niyet gibi davranış varsa 2; ödeme ya da imzalı sözleşme varsa 3; birden çok bağımsız müşteride tekrar eden ödeme varsa 4. Kartların hiçbirinde ödeyen müşteri yoksa 3 ve 4 verilmez.
- Geçmiş emek puan getirmez. Ters yönlü kriterlerde yük ya da risk azaldıkça puan artar.
- Gerekçe 10-200 karakter; bu seçeneğe özgü olguyu söyle (ör. "kamuya açık rakip fiyatı var, alıcı bugün danışmana ödüyor"), genel cümle yazma. Gizlilik kurallarına uy: kişi, müşteri, işveren adı yok.

## Çıktı
`data/final/<KRITER>.json`:
```json
{"kriter": "<KRITER>", "puanlar": {"<seçenek kimliği>": {"p": 3, "k": 1, "g": "…"}}}
```
`data/calib/<KRITER>.json` içindeki bütün seçenek kimlikleri eksiksiz yer almalı. Uzun tek yazma çağrısından kaçın: 40'ar seçeneklik parçalar halinde yaz (ilk parçada dosyayı oluştur, sonra Python ile okuyup `puanlar` sözlüğüne ekleyerek kaydet). Doğrula:
```
python3 tools/validate.py final data/final/<KRITER>.json
```

## Dönüş
Düz metin, 4-6 satır: puan dağılımı (0-5 ve bilinmiyor adetleri), A ya da B'den en az 2 puan farklı verdiğin seçenek sayısı, kanıt kodu dağılımı, en yüksek puan verdiğin üç seçenek, doğrulama sonucu.
