# TRENDYOL SCRAPING ARCHITECTURE

Modüler ve genişletilebilir bir veri çekme mimarisi. Arama terimi bazlı scraping yapısı ile ürün detayları, görseller ve JSON kayıtları organize şekilde toplanır.


## 📁 DOSYA YAPISI

TUSAD <br><br/>
&nbsp;&nbsp;&nbsp;&nbsp;├── trendyol_scraper/      
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── driver.py           
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── fetcher.py           
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── parser.py            
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── downloader.py        
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── search_scraper.py   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── config.py            
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── init.py            
&nbsp;&nbsp;&nbsp;&nbsp;├── Trendyol_Urunler/  
&nbsp;&nbsp;&nbsp;&nbsp;├── venv/             
&nbsp;&nbsp;&nbsp;&nbsp;├── main.py   
&nbsp;&nbsp;&nbsp;&nbsp;├── .gitignore               
&nbsp;&nbsp;&nbsp;&nbsp;├── README.md           
&nbsp;&nbsp;&nbsp;&nbsp;├── requirements.tx            

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
      
| main.py             |      
| driver.py           |      
| fetcher.py          |      
| parser.py           |      
| downloader.py       |       
| search_scraper.py   |       
| config.py           |       
| __init__.py         |       


## 📦 ÇIKTI ÖRNEĞİ

Trendyol_Urunler/    
&nbsp;&nbsp;&nbsp;&nbsp;├── Elbise/    
&nbsp;&nbsp;&nbsp;&nbsp;├── Elbise_0.jpg    
&nbsp;&nbsp;&nbsp;&nbsp;├── Elbise_1.jpg    
&nbsp;&nbsp;&nbsp;&nbsp;└── data.json    



## 🛠️ GELİŞTİRME NOTLARI
- Kod sade, üretime dönük ve modüler yapıdadır
- Gereksiz dosya üretimi engellenmiştir
- trendyol_scraper/ klasörü paket olarak tanımlanmıştır
- main.py dışarıda konumlanır ve modülleri trendyol_scraper. ile çağırır

## 👤 YAZAR
Esisya
Avrupa moda e-ticaretinde otomasyon ve veri çıkarımı uzmanı
Scraping pipeline ve modül mimarisi üzerine üretime dönük çözümler geliştirir..
