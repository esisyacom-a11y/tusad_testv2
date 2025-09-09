# trendyol_scraper/parser.py
from bs4 import BeautifulSoup
import json
import datetime
import time
import requests
from selenium.webdriver.common.by import By
from .config import PRODUCT_TITLE_CSS, BRAND_NAME_CSS, SELLER_NAME_CSS, SELLER_RATING_CSS


class ProductParser:
    """HTML ve JSON-LD verilerini ayrıştırır."""

    def __init__(self, driver):
        self.driver = driver

    def parse_product_list(self, html_source):
        """Ürün listesi sayfasını ayrıştırır."""
        soup = BeautifulSoup(html_source, "html.parser")
        return soup.find_all("div", {"class": "p-card-wrppr"})

    def parse_product_details(self, url):
        """Tek bir ürün sayfasından metin verilerini çeker ve döndürür."""
        print(f"     -> Ürün detayları çekiliyor: {url}")

        try:
            # Önce JSON-LD verisini requests ile hızlıca çekme
            html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")

            json_ld_data = None
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get("@type") == "Product":
                        json_ld_data = data
                        break
                except:
                    continue

            price, discount = None, None
            rating, review_count = None, None

            if json_ld_data:
                if "offers" in json_ld_data:
                    offer = json_ld_data["offers"]
                    if "@type" in offer and offer["@type"] == "AggregateOffer":
                        price = f"{offer.get('price')} TL"
                        discount = f"{offer.get('highPrice')} TL" if 'highPrice' in offer else None
                    elif "@type" in offer and offer["@type"] == "Offer":
                        price = f"{offer.get('price')} TL"

                if "aggregateRating" in json_ld_data:
                    rating_data = json_ld_data["aggregateRating"]
                    rating = rating_data.get("ratingValue")
                    review_count = rating_data.get("reviewCount")

            # Sonra Selenium ile dinamik verileri çekme
            self.driver.get(url)
            time.sleep(3)  # Sayfanın tamamen yüklenmesi için bekleme

            product_name = self.driver.find_element(By.CSS_SELECTOR, PRODUCT_TITLE_CSS).text
            brand = self.driver.find_element(By.CSS_SELECTOR, BRAND_NAME_CSS).text.strip()
            product_only = product_name.replace(brand, "").strip()
            seller = self.driver.find_element(By.CSS_SELECTOR, SELLER_NAME_CSS).text.strip()
            seller_rating = self.driver.find_element(By.CSS_SELECTOR, SELLER_RATING_CSS).text.strip()

            return {
                "ScrapingDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "URL": url,
                "ProductName": product_name,
                "Brand": brand,
                "Product": product_only,
                "Seller": seller,
                "Seller-rating": seller_rating,
                "Price": price,
                "Discount": discount,
                "Rating": rating,
                "Review Count": review_count
            }

        except Exception as e:
            print(f"     Ürün detayı çekilirken hata oluştu: {e}")
            return None