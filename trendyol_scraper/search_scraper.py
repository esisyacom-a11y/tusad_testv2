import os
import re
import json
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

        # Arama klasörü (resimler için)
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

                # Resim klasörü
                save_folder = os.path.join(self.arama_klasoru, urun_id)
                os.makedirs(save_folder, exist_ok=True)

                # Thumbnail indir
                indirilen_resim_sayisi = self.downloader.download(thumbnails, save_folder, urun_id)
                print(f"   {urun_id} için {indirilen_resim_sayisi} adet resim indirildi.")

                # Ürün detaylarını çek
                urun_bilgisi = self.parser.parse_product_details(urun_url)
                if urun_bilgisi:
                    urun_bilgisi["Size"] = urun_bilgisi.get("Size", [])
                    urun_bilgisi["Material"] = urun_bilgisi.get("Material", "")
                    urun_bilgisi["FabricType"] = urun_bilgisi.get("FabricType", "")
                    urun_bilgisi["Color"] = urun_bilgisi.get("Color", "")
                    urun_bilgisi["image_folder"] = save_folder
                    urun_bilgisi["search_term"] = self.arama_terimi  # Hangi aramadan geldiğini belirt
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
        """Tüm ürünleri ana JSON dosyasına ekler."""
        json_path = os.path.join(MAIN_FOLDER, "tum_urunler.json")

        # Eski veriyi oku (varsa)
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    mevcut_veri = json.load(f)
                except json.JSONDecodeError:
                    mevcut_veri = []
        else:
            mevcut_veri = []

        # Yeni ürünleri ekle
        mevcut_veri.extend(self.urun_datasi)

        # Yaz
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(mevcut_veri, f, ensure_ascii=False, indent=4)

        print(f"  Toplam {len(self.urun_datasi)} ürün 'tum_urunler.json' dosyasına eklendi.")
