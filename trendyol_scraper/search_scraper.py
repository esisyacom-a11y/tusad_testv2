# trendyol_scraper/search_scraper.py
import os
import re
from bs4 import BeautifulSoup
from .config import SEARCH_URL, PRODUCT_LIMIT_PER_SEARCH, MAIN_FOLDER
from .downloader import ImageDownloader
from .fetcher import PageFetcher
from .parser import ProductParser

class SearchScraper:
    """Her bir kategori/arama sayfasını gezerek ürün verilerini çeker."""

    def __init__(self, arama_terimi, driver, downloader: ImageDownloader):
        self.arama_terimi = arama_terimi
        self.arama_url = SEARCH_URL.format(arama_terimi.replace(' ', '+'))
        self.driver = driver
        self.downloader = downloader
        self.fetcher = PageFetcher(self.driver)
        self.parser = ProductParser(self.driver)

        # Arama klasörü
        self.klasor_adi = re.sub(r'[^\w\s]', '', arama_terimi).replace(" ", "_").lower()
        self.arama_klasoru = os.path.join(MAIN_FOLDER, self.klasor_adi)
        os.makedirs(self.arama_klasoru, exist_ok=True)

        self.görülen_urunler = set()
        self.urun_datasi = []

    def scrape(self, limit=PRODUCT_LIMIT_PER_SEARCH):
        print(f"  '{self.arama_terimi}' ürünleri çekiliyor...")
        page = 1
        product_count = 0

        while product_count < limit:
            url_to_scrape = f"{self.arama_url}&pi={page}"
            html_source = self.fetcher.get_dynamic_page(url_to_scrape)

            if not html_source:
                break

            products = self.parser.parse_product_list(html_source)

            if not products:
                print("  Sayfada ürün kartı bulunamadı. Muhtemelen boş bir sayfa.")
                break

            yeni_urun_var = False
            for p in products:
                if product_count >= limit:
                    break

                urun_id = p.get("data-id")
                if not urun_id or urun_id in self.görülen_urunler:
                    continue

                self.görülen_urunler.add(urun_id)
                urun_link_tag = p.find("a", {"class": "p-card-chldrn-cntnr"})
                urun_url = "https://www.trendyol.com" + urun_link_tag.get("href")

                # Ürün detay sayfası
                self.driver.get(urun_url)
                detail_soup = BeautifulSoup(self.driver.page_source, "html.parser")
                thumbnails = detail_soup.find_all("img", {"class": "_carouselThumbsImage_ddecc3e"})

                # Resimlerin kaydedileceği klasör
                save_folder = os.path.join(self.arama_klasoru, urun_id)
                os.makedirs(save_folder, exist_ok=True)

                # Thumbnail'ları indir
                indirilen_resim_sayisi = self.downloader.download(thumbnails, save_folder, urun_id)
                print(f"   {urun_id} için {indirilen_resim_sayisi} adet resim indirildi.")

                # Ürün detaylarını çek
                urun_bilgisi = self.parser.parse_product_details(urun_url)
                if urun_bilgisi:
                    urun_bilgisi["image_folder"] = save_folder
                    self.urun_datasi.append(urun_bilgisi)
                    product_count += 1
                    yeni_urun_var = True

            if not yeni_urun_var:
                print("  Yeni ürün bulunamadı. Döngüden çıkılıyor.")
                break

            page += 1

        print(f"  '{self.arama_terimi}': {product_count} ürün verisi çekildi.")
        self.save_data_to_json()

    def save_data_to_json(self):
        """Çekilen verileri JSON dosyasına kaydeder."""
        json_file_name = f"{self.klasor_adi}.json"
        json_path = os.path.join(self.arama_klasoru, json_file_name)
        with open(json_path, "w", encoding="utf-8") as f:
            import json
            json.dump(self.urun_datasi, f, ensure_ascii=False, indent=4)
        print(f"  '{self.arama_terimi}' verileri JSON'a kaydedildi: {json_path}")
