# TRENDYOL SCRAPING ARCHITECTURE

Modüler ve genişletilebilir bir veri çekme mimarisi. Arama terimi bazlı scraping yapısı ile ürün detayları, görseller ve JSON kayıtları organize şekilde toplanır.


## 📁 DOSYA YAPISI

TUSAD/ 
    ├── trendyol_scraper/      
    # Kod modülleri (.py dosyaları) │   
        ├── driver.py │   
        ├── fetcher.py │   
        ├── parser.py │   
        ├── downloader.py │   
        ├── search_scraper.py │   
        ├── config.py │   
        └── init.py 
    ├── Trendyol_Urunler/      
    # Çıktı klasörü (görseller + JSON) 
    ├── venv/                   
    # Sanal ortam (gitignore ile dışlanır) 
    ├── main.py                 
    # Başlatıcı dosya 
    ├── .gitignore              
    # Gereksiz dosya dışlama kuralları 
    ├── README.md               
    # Proje açıklaması 
    ├── requirements.tx


## ⚙️ KURULUM

# Sanal ortam oluştur
python -m venv venv

# Ortamı aktif et
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Gereken kütüphaneleri yükle
pip install -r requirements.txt

## 🚀 KULLANIM
python main.py

- Kullanıcıdan arama terimi alır
- Sayfa sayfa dolaşır
- Ürün detaylarını çeker
- Görselleri indirir
- JSON formatında kaydeder

## 🧩 MODÜLLER
|  |  | 
| main.py |  | 
| driver.py |  | 
| fetcher.py |  | 
| parser.py |  | 
| downloader.py |  | 
| search_scraper.py |  | 
| config.py |  | 
| __init__.py |  | 


## 📦 ÇIKTI ÖRNEĞİ
Trendyol_Urunler/
├── Elbise/
│   ├── Elbise_0.jpg
│   ├── Elbise_1.jpg
│   └── data.json



## 🛠️ GELİŞTİRME NOTLARI
- Kod sade, üretime dönük ve modüler yapıdadır
- Gereksiz dosya üretimi engellenmiştir
- trendyol_scraper/ klasörü paket olarak tanımlanmıştır
- main.py dışarıda konumlanır ve modülleri trendyol_scraper. ile çağırır

## 👤 YAZAR
Esisya
Avrupa moda e-ticaretinde otomasyon ve veri çıkarımı uzmanı
Scraping pipeline ve modül mimarisi üzerine üretime dönük çözümler geliştirir
