# trendyol_scraper/parser.py
from bs4 import BeautifulSoup
import json
import datetime
import time
import requests
from selenium.webdriver.common.by import By


# NOT: Bu dosya, harici bir config dosyasına bağımlı olmadan çalışması için
# tüm CSS seçicilerini doğrudan içermektedir.
# Bu durum, mimarinin ana prensibi olan 'merkezi konfigürasyon'a aykırıdır,
# ancak isteğiniz üzerine bu şekilde düzenlenmiştir.

class ProductParser:
    """HTML ve JSON-LD verilerini ayrıştırır."""

    def __init__(self, driver):
        self.driver = driver

        # Seçiciler (Selectors) doğrudan sınıf içinde tanımlanmıştır
        self.PRODUCT_TITLE_CSS = "h1.product-title"
        self.BRAND_NAME_CSS = "strong"
        self.SELLER_NAME_CSS = "div.merchant-name"
        self.SELLER_RATING_CSS = "div.score-badge"

        # Fiyat, indirim ve puan için yeni CSS seçici listeleri
        self.PRICE_CSS_LIST = [
            "div.price-container span.discounted",
            "div.ty-plus-price-original-price",
            "span.original"
        ]

        self.DISCOUNT_CSS_LIST = [
            "span.ty-plus-price-discounted-price",
            "span.discounted",
            "p.new-price"
        ]

        self.RATING_CSS_LIST = [
            "span.rating",
            "div.rating",
            "span.summary-text"
        ]

    def parse_product_list(self, html_source):
        """Ürün listesi sayfasını ayrıştırır."""
        soup = BeautifulSoup(html_source, "html.parser")
        return soup.find_all("div", {"class": "p-card-wrppr"})

    def parse_product_details(self, url):
        """Tek bir ürün sayfasından metin verilerini çeker ve döndürür."""
        print(f"     -> Ürün detayları çekiliyor: {url}")

        try:
            # Önce JSON-LD verisini requests ile hızlıca çekme
            price_json, discount_json, rating_json, review_count = None, None, None, None
            try:
                html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
                soup = BeautifulSoup(html, "html.parser")
                scripts = soup.find_all("script", type="application/ld+json")
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict) and data.get("@type") == "Product":
                            if "offers" in data:
                                offer = data["offers"]
                                if "@type" in offer and offer["@type"] == "AggregateOffer":
                                    price_json = f"{offer.get('price')} TL"
                                    discount_json = f"{offer.get('highPrice')} TL" if 'highPrice' in offer else None
                                elif "@type" in offer and offer["@type"] == "Offer":
                                    price_json = f"{offer.get('price')} TL"

                            if "aggregateRating" in data:
                                rating_data = data["aggregateRating"]
                                rating_json = rating_data.get("ratingValue")
                                review_count = rating_data.get("reviewCount")
                            break
                    except:
                        continue
            except Exception as e:
                print(f"     Requests/BS hatası: {e}")

            # Sonra Selenium ile dinamik verileri çekme
            self.driver.get(url)
            time.sleep(3)

            # Selenium ile çekilecek veriler
            product_name, brand, product_only, seller, seller_rating, price, discount, rating = [None] * 8

            try:
                product_name = self.driver.find_element(By.CSS_SELECTOR, self.PRODUCT_TITLE_CSS).text
                brand = self.driver.find_element(By.CSS_SELECTOR, self.BRAND_NAME_CSS).text.strip()
                product_only = product_name.replace(brand, "").strip() if product_name and brand else product_name
                seller = self.driver.find_element(By.CSS_SELECTOR, self.SELLER_NAME_CSS).text.strip()
                seller_rating_el = self.driver.find_element(By.CSS_SELECTOR, self.SELLER_RATING_CSS)
                seller_rating = seller_rating_el.text.strip() if seller_rating_el else "0"
            except Exception as e:
                print(f"     Selenium metin verileri çekilirken hata oluştu: {e}")

            for css_selector in self.PRICE_CSS_LIST:
                try:
                    price_el = self.driver.find_element(By.CSS_SELECTOR, css_selector)
                    price = price_el.text.strip()
                    break
                except:
                    continue

            for css_selector in self.DISCOUNT_CSS_LIST:
                try:
                    discount_el = self.driver.find_element(By.CSS_SELECTOR, css_selector)
                    discount = discount_el.text.strip()
                    break
                except:
                    continue

            for css_selector in self.RATING_CSS_LIST:
                try:
                    rating_el = self.driver.find_element(By.CSS_SELECTOR, css_selector)
                    rating = rating_el.text.strip()
                    break
                except:
                    continue

            final_rating = rating_json if rating_json else rating

            return {
                "ScrapingDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "URL": url,
                "ProductName": product_name,
                "Brand": brand,
                "Product": product_only,
                "Seller": seller,
                "Seller-rating": seller_rating,
                "Price": price_json if price_json else price,
                "Discount": discount_json if discount_json else discount,
                "Rating": final_rating,
                "Review Count": review_count
            }

        except Exception as e:
            print(f"     Ürün detayı çekilirken genel hata oluştu: {e}")
            return None