from bs4 import BeautifulSoup
import datetime
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from trendyol_scraper.utils import get_usd_exchange_rate


class ProductParser:
    """HTML verilerini ayrıştırır ve ürün bilgilerini çeker."""

    def __init__(self, driver):
        self.driver = driver

        self.PRODUCT_TITLE_CSS = "h1.product-title"
        self.BRAND_NAME_CSS = "strong"
        self.SELLER_NAME_CSS = "div.merchant-name"
        self.SELLER_RATING_CSS = "div.score-badge"

        self.PRICE_CSS_LIST = [
            "div.price-container span.discounted",
            "div.ty-plus-price-content div.ty-plus-price-original-price",
            "div.price-view span.discounted",
            "div.campaign-price-content p.old-price",
            "div.price-wrapper div.price-view span.original"
        ]

        self.DISCOUNT_CSS_LIST = [
            "div.ty-plus-price-content span.ty-plus-price-discounted-price",
            "div.campaign-price-content p.new-price",
            "div.price-view span.discounted"
        ]

        self.RATING_CSS_LIST = [
            "span.reviews-summary-average-rating",
            "span[data-testid='average-rating']",
            "div.rating-value",
            "div.rating",
            "span.pr-rnr-rating",
            "div.pr-rnr-rating",
            "span.rating-score"
        ]

        self.REVIEW_COUNT_CSS = "a.reviews-summary-reviews-detail b"

    def _clean_price(self, price_text):
        """Fiyat metnini temizler ve float'a dönüştürür."""
        if not price_text:
            return None
        return price_text.replace("TL", "").replace("₺", "").replace(",", ".").strip()

    def _parse_prices_with_selenium(self):
        """Selenium kullanarak fiyat ve indirimli fiyatı bulur."""
        product_info = {"Price": None, "Discount": None}

        # Fiyatı bul
        for css_selector in self.PRICE_CSS_LIST:
            try:
                price_text = self.driver.find_element(By.CSS_SELECTOR, css_selector).text.strip()
                product_info["Price"] = self._clean_price(price_text)
                break
            except NoSuchElementException:
                continue

        # İndirimli fiyatı bul
        for css_selector in self.DISCOUNT_CSS_LIST:
            try:
                discount_text = self.driver.find_element(By.CSS_SELECTOR, css_selector).text.strip()
                product_info["Discount"] = self._clean_price(discount_text)
                break
            except NoSuchElementException:
                continue

        return product_info

    def parse_product_list(self, html_source):
        """Ürün listesi sayfasını ayrıştırır."""
        soup = BeautifulSoup(html_source, "html.parser")
        return soup.find_all("div", {"class": "p-card-wrppr"})

    def _parse_with_html(self, driver):
        """Selenium'dan alınan HTML'i BeautifulSoup ile ayrıştırır."""

        product_info = {
            "ProductName": None, "Brand": None, "Product": None,
            "Seller": None, "Seller-rating": None, "Price": None,
            "Discount": None, "Rating": None, "Review Count": "0"
        }

        try:
            # Selenium ile fiyat ve indirimleri bul
            selenium_prices = self._parse_prices_with_selenium()
            product_info.update(selenium_prices)

            # Eğer Selenium ile fiyat bulunamadıysa, BeautifulSoup'a devam et
            if not product_info["Price"] and not product_info["Discount"]:
                html_source = driver.page_source
                soup = BeautifulSoup(html_source, "html.parser")
                for css_selector in self.PRICE_CSS_LIST:
                    price_el = soup.select_one(css_selector)
                    if price_el:
                        product_info["Price"] = price_el.text.strip()
                        break
                for css_selector in self.DISCOUNT_CSS_LIST:
                    discount_el = soup.select_one(css_selector)
                    if discount_el:
                        product_info["Discount"] = discount_el.text.strip()
                        break

            # Diğer bilgileri BeautifulSoup ile çek
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, "html.parser")

            product_name_el = soup.select_one(self.PRODUCT_TITLE_CSS)
            if product_name_el:
                product_info["ProductName"] = product_name_el.text.strip()

            brand_el = soup.select_one(self.BRAND_NAME_CSS)
            if brand_el:
                product_info["Brand"] = brand_el.text.strip()
                if product_info["ProductName"]:
                    product_info["Product"] = product_info["ProductName"].replace(product_info["Brand"], "").strip()

            seller_el = soup.select_one(self.SELLER_NAME_CSS)
            if seller_el:
                product_info["Seller"] = seller_el.text.strip()

            seller_rating_el = soup.select_one(self.SELLER_RATING_CSS)
            product_info["Seller-rating"] = seller_rating_el.text.strip() if seller_rating_el else "0"

            for css_selector in self.RATING_CSS_LIST:
                rating_el = soup.select_one(css_selector)
                if rating_el and rating_el.text.strip():
                    product_info["Rating"] = rating_el.text.strip()
                    break

            review_el = soup.select_one(self.REVIEW_COUNT_CSS)
            if review_el and review_el.text.strip():
                match = re.search(r'\d+', review_el.text.replace(".", ""))
                if match:
                    product_info["Review Count"] = match.group(0)

            # Kritik veri yoksa None döndür
            if not product_info["ProductName"] and not product_info["Price"]:
                return None

            # Price ve Discount aynı ise Discount'u None yap
            if product_info["Price"] and product_info["Discount"]:
                if product_info["Price"] == product_info["Discount"]:
                    product_info["Discount"] = None

            return product_info

        except Exception as e:
            print(f"HTML'den veri çekilirken hata oluştu: {e}")
            return None

    def parse_product_details(self, url):
        """Tek bir ürün sayfasından metin verilerini çeker ve döndürür."""
        start_time = time.time()
        print(f"-> Ürün detayları çekiliyor: {url}")
        final_data = {
            "ScrapingDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "URL": url,
            "PriceToDollar": 0.0
        }

        try:
            self.driver.get(url)
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.PRODUCT_TITLE_CSS))
                )
            except TimeoutException:
                pass

            html_data = self._parse_with_html(self.driver)

            if html_data:
                final_data.update(html_data)

                used_price = html_data.get("Discount") if html_data.get("Discount") else html_data.get("Price")
                usd_rate = get_usd_exchange_rate()
                try:
                    if used_price:
                        cleaned_price = float(self._clean_price(used_price))
                        final_data["PriceToDollar"] = round(cleaned_price / usd_rate, 2) if usd_rate else 0.0
                except Exception as e:
                    print(f"Fiyat dolar dönüşümünde hata: {e}")
                    final_data["PriceToDollar"] = 0.0

                elapsed_time = round(time.time() - start_time, 2)
                print(f"-> İşlem tamamlandı. Geçen süre: {elapsed_time} saniye\n")
                return final_data

            print("-> HTML'den veri çekilemedi!")
            return None

        except Exception as e:
            elapsed_time = round(time.time() - start_time, 2)
            print(f"Ürün detayı çekilirken hata: {e}. Geçen süre: {elapsed_time} saniye\n")
            return None
