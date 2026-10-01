# Hakem brifi: kapı ve finans itirazlarının karara bağlanması

Bir projenin ticari seçenek kartını bir analist yazdı. Bağımsız ikinci değerlendirici karttaki bazı kapı durumlarına ve finans girdilerine itiraz etti. Sen hakemsin: her itirazı kaynak belgelere göre karara bağlayacak ve gerekiyorsa kartı düzelteceksin. Puanlara dokunma; onlar ayrı bir adımda ele alınıyor.

## Oku
1. `briefs/GIZLILIK.md`, `briefs/KRITERLER.md` (kapı tanımları) ve `briefs/BRIEF_ANALIST.md` içindeki "Finans girdileri" bölümü.
2. Kart: `data/cards/<slug>.json`.
3. İkinci değerlendiricinin dosyası: `data/scores/<slug>.B.json` içindeki `kart_itirazlari`, `kapi_itirazlari`, `finans_itirazlari` listeleri (puanlara bakma).
4. Görevde verilen kaynak belgeler.

## Karar ver
Her itiraz için: kaynak belge hangi tarafı destekliyor?
- İtiraz haklıysa kartta ilgili alanı düzelt (kapı durumu ve notu, finans rakamı, tanım alanı). Finans rakamı değişirse bağlı rakamları da tutarlı hale getir (tahsilat = ödeme adedi × net fiyat mantığı; kötü ≤ baz ≤ iyi; kalan efor min ≤ beklenen ≤ max) ve `dayanak` metnini güncelle.
- İtiraz haksızsa kartı değiştirme.
- Kaynak iki tarafı da desteklemiyorsa temkinli olanı seç: kapıda "test", finansta düşük gelir ve yüksek efor.
Ayrıca kartı kendi gözünle bir kez tara: kapı tanımına göre açıkça yanlış duran bir durum (ör. yazılı izin gerektiren üçüncü taraf kodu için G1 "gecti") ya da kaynakla çelişen bir rakam görürsen onu da düzelt.

## Çıktı
1. Güncellenmiş kart: `data/cards/<slug>.json` (aynı şema; seçenek kimliklerini ve sayısını değiştirme). Düzenlemeyi Python ile dosyayı okuyup alanı değiştirerek yap; dosyayı baştan yazma.
2. Karar kaydı: `data/hakem/<slug>.json`:
```json
{"slug": "<slug>", "kararlar": [{"itiraz": "≤ 200 karakter", "karar": "kabul | ret | kismen", "degisiklik": "≤ 200: hangi alan neydi, ne oldu; ret ise boş metin", "gerekce": "≤ 200"}]}
```
Doğrula:
```
python3 tools/validate.py kart data/cards/<slug>.json
python3 tools/validate.py hakem data/hakem/<slug>.json
```

## Dönüş
Düz metin, 3-5 satır: kaç itiraz, kaçı kabul edildi, karttaki önemli değişiklikler, doğrulama sonucu.
