# Görsel referans değişiklikleri

Her satır, ilk üretimden sonra değiştirilen bir görsel referansı ve gerekçesini kaydeder. Önce ve sonra görüntüleri bu klasördedir.

| Referans | Gerekçe | Önce | Sonra |
|---|---|---|---|
| `*/kapilar-320.png`, `*/kapilar-390.png`, `*/kapilar-1280.png` ve aynı testteki `kriterler-*.png` | Test düzeneği hatası: sayfanın kaydırma boşluğu yüzünden görünüm alanına tam sığmayan kapılar listesinin son satırı 390 genişlikte kırpılıyordu. Öğe görüntüleri artık uzatılmış bir görünüm alanında alınıyor (genişlik ve yerleşim aynı). Diğer genişliklerde fark alt piksel konumundan geliyor; içerik aynı. Aynı değişiklikte yüzde 1'lik piksel toleransı kaldırıldı, çünkü kırpılmış bir satırı gizleyebiliyordu. | `<profil>-kapilar-<genişlik>-once.png` | `<profil>-kapilar-<genişlik>-sonra.png` |
| `webkit/odak-dugme-390.png` | Test hatası: macOS WebKit'te Tab düğmelerde durmadığı için ilk referans odaksız bir ekranı kaydetmişti. Test, WebKit'te Option+Tab kullanacak ve ekran görüntüsünden önce odağı doğrulayacak biçimde düzeltildi; yeni referansta odak çerçevesi görünüyor. | `webkit-odak-dugme-390-once.png` | `webkit-odak-dugme-390-sonra.png` |

| Bütün referans seti | Depo sahibinin istediği arayüz düzenlemesi: proje sayfası "Bu proje nedir?" yanıtıyla açılıyor, proje listesi harf sıralı bir sözlüğe dönüştü, özet sayfasına eleme hunisi geldi, bölümler çizgi yerine boşluk ve zemin tonuyla ayrılıyor, kapı işaretlerinin metni görünür oldu. Aynı geçişte bağımsız QA bulguları düzeltildi ve yeni referanslar eklendi (menü açık, bölüm gezintisinde odak, değer tablosu, yatay telefon, tablet, şablonun geniş ekranı). Eski set bir önceki commit'te duruyor. | `qa/ux-oncesi/` | `qa/ux-sonrasi/` |

Bu değişiklikleri uygulayıcı kaydetti; depo sahibinin onayı bekleniyor.
