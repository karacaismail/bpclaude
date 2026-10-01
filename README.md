# bpclaude

Reklam vermeden, bir ile altı ay arasında birkaç bin dolar nakit getirecek projeyi seçmek için kurulmuş bir seçim şablonu ve bu şablonla yapılmış bir puanlama.

Site: `docs/` klasöründen GitHub Pages ile yayımlanır.

## İçinde ne var

- **Şablon.** Sekiz telafi edilemez kapı, altı kategoride 26 kriter (0-5, davranışla tanımlanmış çapalar), puandan ayrı tutulan kanıt ölçeği (E0-E4), altı aylık nakit hesabı ve ayrı bir stratejik eksen.
- **Puanlama.** 45 proje, 132 ticari seçenek. Her seçenek iki bağımsız değerlendirici tarafından puanlandı, itirazlar bir hakem tarafından karara bağlandı, her kriter bütün seçenekler boyunca tek elden kalibre edildi.
- **Çalışma kitabı.** `docs/indir/bpclaude-secim-sablonu.xlsx`: formüllü. Ağırlık, puan, kanıt kodu ya da finans girdisi değişince sıralama yeniden hesaplanır.
- **Proje sözlüğü.** Her proje için "bu nedir?" sorusunun beş parçalı yanıtı: ne tür bir şey, kim için, hangi işi görür, nasıl çalışır, bugün nerede. Kaynak belgelerden yazıldı.
- **Site.** Özet, sıralama, proje sözlüğü ve proje sayfaları, şablon, tanı soruları, duyarlılık, portföy, indirme ve yöntem.

## Nasıl okunmalı

Puan bir başarı olasılığı değildir. Hiçbir seçenekte ödeyen müşteri kanıtı yoktur; rakamların çoğu kaynak belgelerdeki varsayımlardır. Puanlar yapay zekâ ajanları tarafından verildi; kurucunun kendi bilgisi (özellikle ilk alıcılara doğrudan erişim) çalışma kitabına işlendiğinde sıra değişebilir. Doğru kullanım: kısa listeden bir ya da iki seçeneği seçip deney kartındaki testi yapmak ve sonucu çalışma kitabına işlemek.

## Kaynaklar

İki ayrı iş fikri çalışması (yalnız okundu, değiştirilmedi) ve aynı soruya verilmiş üç yanıt: bir Claude araştırması, bir ChatGPT araştırması ve bir sohbet yanıtı. Kaynak belgeler bu depoda yer almaz.

## Yayın kuralları

Depo herkese açıktır. Kişi, müşteri, işveren ve üçüncü taraf adları yazılmadı; adı verilmeyen tarafları tanınır kılacak ayrıntılar genelleştirildi. Hukuki ya da etik nedenle iş fikri sayılmayan klasörler alınmadı. İki değerlendiricinin ham gerekçeleri yayımlanmadı; puanları, kanıt kodları ve her kriterin son gerekçesi depodadır. Ayrıntı: sitedeki Hakkında sayfası ve `AGENTS.md`.

## Derleme ve test

```bash
npm ci
```

```bash
npm run build
```

```bash
npm test
```

Gerekenler: Python 3.9 ve üstü (`openpyxl`, `formulas`), Node 24. Komutların tamamı ve çalışma kuralları `AGENTS.md` içindedir. `private/` klasörü depoda yoktur; bu yüzden depodan alınan bir kopyada yayın taraması eksik sayılır ve `npm run build` son adımda uyarı verir.

## Lisans

Lisans henüz seçilmedi. Açık görünürlük bir lisans değildir; seçilene kadar içerik için yeniden kullanım izni verilmiş sayılmaz.
