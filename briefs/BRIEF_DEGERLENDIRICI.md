# İkinci değerlendirici brifi: bağımsız puanlama

Bir projenin ticari seçenekleri bir analist tarafından tanımlandı ve puanlandı. Sen **bağımsız ikinci değerlendiricisin**: analistin puanlarını görmeden, aynı seçenekleri aynı ölçekle kendin puanlayacaksın. Amaç tek bir değerlendiricinin önyargısını ve gürültüsünü azaltmak; iki puan sonra karşılaştırılacak. Analistin puan dosyasını (`data/scores/<slug>.A.json`) AÇMA.

## Oku
1. `briefs/GIZLILIK.md` ve `briefs/KRITERLER.md`.
2. Kart: `data/cards/<slug>.json` (seçenek tanımları, kapılar, finans girdileri, kanıt notları).
3. Görevde verilen kaynak belgeler (Claude planı ve derinlik dosyası, GPT strateji dosyaları). Kartta yazanı kaynakla karşılaştır; kart bir gerçeği abartmış ya da atlamışsa puanını kaynağa göre ver ve `kart_itirazlari` listesine yaz.

## Puanla
Her seçenek için 26 kriter (A1-F3) ve 4 stratejik kriter (S1-S4): `p` (0-5 tam sayı ya da dayanak hiç yoksa `null`), `k` kanıt kodu (0-4), `g` gerekçe (10-200 karakter; belge ve bölüm).
- Şüpheci ol: iddia kaynakta bir rakamla ya da olguyla desteklenmiyorsa kanıt 0'dır ve puan 3'ü geçmez.
- Çapaya göre puanla; kriter kriter düşün, genel izlenimi kriterlere yayma.
- Geçmiş emek puan getirmez; "kod var" ödeme isteği kanıtı değildir. Ödeyen müşteri yoksa A6 en çok 3, kanıtı en çok 1.
- Ters yönlü kriterlerde (B6, C2, C3, C6, F1, F2, F3) yük ya da risk azaldıkça puan artar.
- Kapıları da kendin değerlendir: karttaki kapı durumuna katılmıyorsan `kapi_itirazlari` listesine "seçenek kimliği, kapı, senin durumun, gerekçe" yaz.
- Finans girdilerinde kaynağa göre açıkça iyimser bir rakam görürsen `finans_itirazlari` listesine yaz (hangi alan, kartta ne, sence ne, neden).

## Çıktı
`data/scores/<slug>.B.json`:
```json
{"slug": "<slug>", "degerlendirici": "B",
 "puanlar": {"<seçenek kimliği>": {"A1": {"p": 3, "k": 1, "g": "…"}, "…": {}}},
 "kart_itirazlari": ["≤ 200 karakterlik maddeler"], "kapi_itirazlari": ["…"], "finans_itirazlari": ["…"]}
```
İtiraz yoksa boş liste yaz. Tek çağrıda 150 satırdan uzun metin yazma; seçenek seçenek yaz. Doğrula:
```
python3 tools/validate.py puan data/scores/<slug>.B.json
```

## Dönüş
Düz metin, 4-6 satır: dosya, seçenek başına ağırlıksız ortalama puanın, en düşük puan verdiğin üç kriter ve nedeni, itiraz sayıları, doğrulama sonucu.
