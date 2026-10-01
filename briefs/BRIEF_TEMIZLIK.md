# Temizlik brifi: yayın öncesi metin düzeltmesi

Bu çalışmanın verisi herkese açık bir sitede ve herkese açık bir Git deposunda yayımlanacak. Kartlar, hakem kararları ve teslim notları bağımsız denetçilerce okunup düzeltildi. Sitede her kriterin yanında görünen kriter gerekçeleri (`data/final`) ise henüz okunmadı. Senin işin bunları okumak ve kartlarda kalan izleri bulmak.

## Oku
1. `briefs/GIZLILIK.md`
2. Görevde verilen her proje için:
   - `data/cards/<slug>.json`: düzeltilmiş kart. Aynı bilginin artık nasıl yazıldığını buradan gör.
   - `private/temizlik/girdi/<slug>.json`: o projenin bütün kriter gerekçeleri (`final`) ve dikkat edilecek ifadeler (`ipuclari`). İpuçları otomatik çıkarıldı; çoğu zararsızdır, yalnız bakılacak yeri gösterir.

## Ne arıyorsun
Denetçilerin kartlarda bulduğu türler, gerekçelerde başka sözcüklerle tekrar ediyor olabilir:
- Adı verilmeyen müşteriyi tanınır kılan ayrıntı: kesin şube, sayfa, dil ya da çalışan sayısı; şube tipleri; müşterinin iç süreci (yeni personel, satıcı tekliflerinin süresi, askıdaki kararları, onay eşiği); müşteriye teslim edilmiş analizin içeriği.
- Müşteri işinden türeyen kod ya da içerik; müşteriye yapılmış rakip analizinin satış listesi olarak kullanılması.
- İşveren, fikri mülkiyet ve çıkar çatışması notları; kurucunun başka bir işe bağlı olduğunu ima eden ifadeler.
- Hukuki risk itirafı: telif (kitap seçkisi, tam metin), lisans ihlali (ticari tema kalıntısı), uydurma yorum, platform kurallarına aykırı taktik (ilanlardan telefon toplama, randevu botu).
- Güvenlik ya da operasyon ayrıntısı: yedek, sır, gönderilmemiş commit, tek makineye bağlı üretim.
- Üçüncü tarafın iç rakamı (ör. bir kitabın satış adedi) ya da kişisel mali bilgi (ör. sigorta erteleme).
- Yerel dosya ya da klasör adı (alt çizgili kaynak adları).
- Adı geçen rakip hakkında kaynaksız olumsuz iddia.
- Eski eşik: modelin eşik saat ücreti artık 500 ₺. "750 TL eşik" gibi atıfları sayısız "eşik saat ücreti" diye yaz ya da 500 ₺ ile doğru kalıyorsa 500 yaz.

Yanlış alarm verme. Şunlar serbesttir: kamuya açık rakip, araç, pazar yeri, kurum ve şehir adları; kurucunun kendi teklif ve fiyatları; "kurucu", "bir kahve zinciri", "bir inşaat firması", "üçüncü taraf bir şirket" gibi tanımlar; puan, kanıt düzeyi ve plan bölüm numaraları.

## Nasıl düzeltirsin
- Puanı, kanıt kodunu ve gerekçenin anlamını değiştirme; yalnız ifadeyi nötrleştir. Aynı bilgi kartta nasıl yazıldıysa ona uy.
- En küçük değişikliği yap. `eski`, hedef metnin içinden harf, boşluk ve noktalamasıyla birebir kopyalanmış en kısa parçadır. Değişiklikten sonra gerekçe 10-200 karakter kalmalı.
- Değiştirilecek bir şey yoksa boş liste yaz. Gereksiz değişiklik önerme.

## Çıktı
Her proje için `private/temizlik/cikti/<slug>.json`:
```json
{"slug": "<slug>", "degisiklikler": [
  {"dosya": "final", "secenek": "<seçenek kimliği>", "kriter": "<KRITER>", "eski": "…", "yeni": "…", "tur": "tanınır kılan ayrıntı"},
  {"dosya": "kart", "secenek": null, "kriter": null, "eski": "…", "yeni": "…", "tur": "hukuki risk"}
]}
```
`dosya`: `final`, `kart`, `hakem` ya da `teslim`. Her dosyayı doğrula:
```
python3 tools/temizlik.py check private/temizlik/cikti/<slug>.json
```
TAMAM yazana dek düzelt. `data/` altındaki dosyaları değiştirme; değişiklikler merkezde uygulanacak. Başka dosyaya yazma, alt ajan başlatma, web araması yapma. Emoji yok.

## Dönüş
Proje başına bir satır: önerilen değişiklik sayısı ve türlere göre dağılım; emin olmadığın durumlar.
