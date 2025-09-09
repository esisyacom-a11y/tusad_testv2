import os
from config import KATEGORILER
from driver import get_driver
from downloader import ImageDownloader
from category_scraper import CategoryScraper
"""KULLANICIDAN ARAMA TERİMİ ALIR VE SCRAPING SÜRECİNİ BAŞLATIR."""

def run_scraper():
    ana_klasor = "Trendyol_Urunler"
    os.makedirs(ana_klasor, exist_ok=True)

    driver = get_driver(headless=True)
    downloader = ImageDownloader()

    try:
        for kategori_adi, kategori_url in KATEGORILER.items():
            scraper = CategoryScraper(
                kategori_adi=kategori_adi,
                kategori_url=kategori_url,
                ana_klasor=ana_klasor,
                driver=driver,
                downloader=downloader
            )
            scraper.scrape(limit=5)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()