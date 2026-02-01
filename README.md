# fetchBlog

Sitemap'lerden URL toplayan, sayfaları tarayıp H1–H6 başlıklarını filtreleyen ve bunları MySQL veritabanına kaydeden Python betiği.

## Ne Yapar?

- **Sitemap okuma:** Yapılandırılmış sitemap URL'lerinden tüm sayfa linklerini çeker.
- **Sayfa tarama:** Her URL'yi ziyaret eder, HTML'i parse eder.
- **Başlık çıkarma:** Sadece `h1`–`h6` etiketlerindeki metinleri alır.
- **Filtreleme:** Başlıklar anahtar kelimelere göre seçilir; domain içeren veya yasaklı kelime içeren satırlar atlanır.
- **Veritabanı:** Benzersiz `(title, url)` çiftleri MySQL'deki `headings` tablosuna yazılır.

## Gereksinimler

- Python 3.7+
- MySQL sunucusu (erişilebilir olmalı)
- İnternet bağlantısı

## Kurulum

```bash
# Sanal ortam (isteğe bağlı)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS

# Bağımlılıkları yükle
pip install -r requirements.txt
```

## Yapılandırma

`main.py` içindeki şu bölümü kendi ortamınıza göre düzenleyin:

| Değişken | Açıklama |
|----------|----------|
| `SITEMAP_URLS` | Taranacak sitemap XML URL'leri |
| `KEYWORDS` | Başlıkta bulunması gereken kelimeler (örn. `"rüya"`, `"ruya"`) |
| `IGNORE_LIST` | Başlıkta geçerse kayıt atlanacak kelimeler |
| `DB_CONFIG` | MySQL bağlantı bilgileri: `host`, `user`, `password`, `database` |

**Güvenlik:** Veritabanı şifresini kod içinde bırakmak yerine ortam değişkeni kullanmanız önerilir.

## Çalıştırma

```bash
python main.py
```

Betik sırayla:

1. Veritabanına bağlanır, gerekirse veritabanı ve `headings` tablosunu oluşturur.
2. Tüm sitemap'lerden URL'leri toplar.
3. Her URL için sayfayı çeker, başlıkları filtreler ve yeni kayıtları tabloya yazar.
4. İşlem bitince bağlantıyı kapatır.

## Veritabanı Tablosu

`headings` tablosu örnek yapı:

| Alan | Tip | Açıklama |
|------|-----|----------|
| `id` | INT, AUTO_INCREMENT | Birincil anahtar |
| `title` | TEXT | Başlık metni (H1–H6) |
| `url` | VARCHAR(500) | Sayfa URL'si |
| `timestamp` | TIMESTAMP | Kayıt zamanı |

`title` alanında benzersizlik (255 karakter) zorunludur; aynı başlık tekrar eklenmez.

## Bağımlılıklar (requirements.txt)

- **requests** — HTTP istekleri
- **beautifulsoup4** — HTML parse
- **lxml** — BeautifulSoup için XML/HTML parser
- **mysql-connector-python** — MySQL bağlantısı

## Lisans

Bu proje kişisel/kullanım amaçlı paylaşılmıştır.
