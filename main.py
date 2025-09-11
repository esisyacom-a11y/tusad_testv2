# main.py
import time
import sys
import pandas as pd
import os
from trendyol_scraper.driver import WebDriverManager
from trendyol_scraper.downloader import ImageDownloader
from trendyol_scraper.search_scraper import SearchScraper
from trendyol_scraper.config import BASE_URL, EXCEL_FILE_PATH, MAIN_FOLDER

def main():

    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        search_list = [str(item).lower().strip() for item in df['Kategori'].tolist() if pd.notna(item)]
        if not search_list:
            print("Excel dosyasında kategori bulunamadı. Lütfen 'Kategori' sütununu doldurun.")
            sys.exit()
        else:
            print("Kategoriler Excel dosyasından başarıyla yüklendi.")

    except FileNotFoundError:
        print(f"Hata: '{EXCEL_FILE_PATH}' dosyası bulunamadı. Lütfen dosyayı doğru konuma yerleştirin.")
        sys.exit()
    except Exception as e:
        print(f"Hata: Dosya okunurken bir hata oluştu: {e}")
        sys.exit()

    driver_manager = WebDriverManager()
    downloader = ImageDownloader()

    try:
        driver = driver_manager.get_driver()
        driver.get(BASE_URL)
        driver_manager.accept_cookies()

        os.makedirs(MAIN_FOLDER, exist_ok=True)

        for arama_terimi in search_list:
            scraper = SearchScraper(arama_terimi, driver, downloader)
            scraper.scrape(limit=5)



    finally:
        driver_manager.quit_driver()
        print("Tarayıcı kapatıldı. İşlem tamamlandı.")


if __name__ == "__main__":
    main()