import os
import json
from bs4 import BeautifulSoup
from parser import parse_product_details

class CategoryScraper:
    def __init__(self, kategori_adi, kategori_url, ana_klasor, driver, downloader):
        self.kategori_adi = kategori_adi
        self.kategori_url = kategori_url
        self.ana_klasor = ana_klasor
        self.driver = driver
        self.downloader = downloader
        self.kategori_klasor = os.path.join(ana_klasor, kategori_adi)
        os.makedirs(self.kategori_klasor, exist_ok=True)
        self.görülen_urunler = set()
        self.urun_datasi = []

    def scrape(self, limit=5):
        print(f"  {self.kategori_adi} ürünleri çekiliyor...")
        page = 1
        product_count = 0

        while product_count < limit:
            self.driver.get(f"{self.kategori_url}?pi={page}")
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            products = soup.find_all("div", {"class": "p-card-wrppr"})
            if not products:
                break

            for p in products:
                if product_count >= limit:
                    break

                urun_id = p.get("data-id")
                if not urun_id or urun_id in self.görülen_urunler:
                    continue
                self.görülen_urunler.add(urun_id)

                urun_link_tag = p.find("a", {"class": "p-card-chldrn-cntnr"})
                urun_url = "https://www.trendyol.com" + urun_link_tag.get("href")

                # Görsel indir
                img_tag = p.find("img")
                img_path = None
                if img_tag and "src" in img_tag.attrs:
                    img_url = img_tag["src"]
                    img_name = f"{self.kategori_adi}_{product_count}.jpg"
                    img_path = os.path.join(self.kategori_klasor, img_name)
                    if self.downloader.download(img_url, img_path):
                        print(f"   -> Resim kaydedildi: {img_path}")

                # Ürün detaylarını çek
                urun_bilgisi = parse_product_details(self.driver, urun_url)
                if urun_bilgisi:
                    urun_bilgisi["image_path"] = img_path
                    self.urun_datasi.append(urun_bilgisi)
                    product_count += 1

            page += 1

        self.save_data_to_json()

    def save_data_to_json(self):
        json_path = os.path.join(self.kategori_klasor, "data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.urun_datasi, f, ensure_ascii=False, indent=4)
        print(f"  {self.kategori_adi} verileri JSON'a kaydedildi: {json_path}")
