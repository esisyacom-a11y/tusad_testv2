from bs4 import BeautifulSoup
import json
import datetime
import time
import requests
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from trendyol_scraper.utils import get_usd_exchange_rate


class ProductParser:
    """HTML, JSON-LD ve JavaScript verilerini ayrıştırır."""

    def __init__(self, driver):
        self.driver = driver

        self.PRODUCT_TITLE_CSS = "h1.product-title"
        self.BRAND_NAME_CSS = "strong"
        self.SELLER_NAME_CSS = "div.merchant-name"
        self.SELLER_RATING_CSS = "div.score-badge"

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
            "span[data-testid='average-rating']",
            "div.pr-rnr-sm-p div.rnr-com-stars",
            "div.rating-value",
            "div.rating",
            "span.pr-rnr-rating",
            "div.pr-rnr-rating",
            "span.rating-score"
        ]

        self.REVIEW_COUNT_CSS_LIST = [
            "span[data-testid='total-comments-desktop']",
            "div.pr-rnr-sm-p span.pr-rnr-sm-p",
            "div.rating-review-count",
            "div.reviews-count-text",
            "div.pr-in-cnr div.pr-rnr-sm-p > span",
            "span.pr-rnr-comment-count",
            "span.total-review-count",
            "div.product-review-count"
        ]

    def parse_product_list(self, html_source):
        """Ürün listesi sayfasını ayrıştırır."""
        soup = BeautifulSoup(html_source, "html.parser")
        return soup.find_all("div", {"class": "p-card-wrppr"})

    def _parse_with_html(self, driver):
        """Selenium ile HTML elementlerini çekmeye çalışır."""
        product_info = {
            "ProductName": None, "Brand": None, "Product": None,
            "Seller": None, "Seller-rating": None, "Price": None,
            "Discount": None, "Rating": None, "Review Count": None,
            "DataSource": "HTML"
        }

        try:
            # Temel ürün bilgilerini çekme
            product_info["ProductName"] = driver.find_element(By.CSS_SELECTOR, self.PRODUCT_TITLE_CSS).text
            product_info["Brand"] = driver.find_element(By.CSS_SELECTOR, self.BRAND_NAME_CSS).text.strip()
            product_info["Product"] = product_info["ProductName"].replace(product_info["Brand"], "").strip()
            product_info["Seller"] = driver.find_element(By.CSS_SELECTOR, self.SELLER_NAME_CSS).text.strip()

            try:
                seller_rating_el = driver.find_element(By.CSS_SELECTOR, self.SELLER_RATING_CSS)
                product_info["Seller-rating"] = seller_rating_el.text.strip()
            except NoSuchElementException:
                product_info["Seller-rating"] = "0"

            # Fiyat ve indirim çekme (Liste ile deneme)
            for css_selector in self.PRICE_CSS_LIST:
                try:
                    product_info["Price"] = driver.find_element(By.CSS_SELECTOR, css_selector).text.strip()
                    break
                except NoSuchElementException:
                    continue

            for css_selector in self.DISCOUNT_CSS_LIST:
                try:
                    product_info["Discount"] = driver.find_element(By.CSS_SELECTOR, css_selector).text.strip()
                    break
                except NoSuchElementException:
                    continue

            # Rating ve Review Count çekme (Liste ile deneme)
            wait = WebDriverWait(driver, 2)
            try:
                no_review_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.summary-text")))
                if "Henüz Yorum Yazılmamış" in no_review_el.text.strip() or re.search(r"0\s*(yorum|değerlendirme)",
                                                                                      no_review_el.text, re.IGNORECASE):
                    product_info["Rating"] = "0"
                    product_info["Review Count"] = "0"
            except TimeoutException:
                for css_selector in self.RATING_CSS_LIST:
                    try:
                        product_info["Rating"] = wait.until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))).text.strip()
                        break
                    except:
                        continue

                for css_selector in self.REVIEW_COUNT_CSS_LIST:
                    try:
                        text = wait.until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector))).text.strip()
                        match = re.search(r'\d+', text)
                        if match:
                            product_info["Review Count"] = match.group(0)
                        break
                    except:
                        continue

            # Kontrol: Eğer kritik veriler çekilemediyse None döndür
            if not product_info["ProductName"] or not product_info["Price"]:
                return None

            return product_info

        except Exception as e:
            print(f"     HTML'den veri çekilirken hata oluştu: {e}")
            return None

    def parse_product_details(self, url):
        """Tek bir ürün sayfasından metin verilerini çeker ve döndürür."""
        start_time = time.time()
        print(f"     -> Ürün detayları çekiliyor: {url}")
        final_data = {"ScrapingDate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "URL": url}

        try:
            # 1. Aşama: HTML'den veri çekmeyi dene (Öncelikli yöntem)
            print("     -> Önce HTML'den veri çekiliyor...")
            self.driver.get(url)

            # Kademeli scroll yap
            for i in range(3):  # Daha az scroll
                self.driver.execute_script(f"window.scrollTo(0, {(i + 1) * 3000});")
                time.sleep(0.5)  # Bekleme süresi daha da kısaltıldı

            html_data = self._parse_with_html(self.driver)

            if html_data:
                final_data.update(html_data)
                print(f"     -> HTML'den veri çekimi başarılı. Kaynak: {final_data['DataSource']}.")
                end_time = time.time()
                elapsed_time = round(end_time - start_time, 2)
                print(f"     -> İşlem tamamlandı. Geçen süre: {elapsed_time} saniye\n")

                used_price = html_data.get("Discount") if html_data.get("Discount") else html_data.get("Price")
                usd_rate = get_usd_exchange_rate()
                try:
                    if used_price:
                        cleaned_price = float(used_price.replace("TL", "").replace("₺", "").replace(",", ".").strip())
                        final_data["PriceToDollar"] = round(cleaned_price / usd_rate, 2) if usd_rate else None
                    else:
                        final_data["PriceToDollar"] = None
                except Exception as e:
                    print(f"     Fiyat dolar dönüşümünde hata: {e}")
                    final_data["PriceToDollar"] = None

                return final_data

            # 2. Aşama: HTML ile başarısız olunursa JavaScript'i dene
            print("     -> HTML'den veri çekilemedi. JavaScript deniyor...")
            final_data["DataSource"] = "JavaScript"
            rating_js, review_count_js = None, None
            try:
                js_data_list = [
                    "return window.__TLC_PRODUCTS_APP_DATA__;",
                    "return window.__INITIAL_STATE__;",
                    "return window.__PRODUCT_DETAIL_APP_INITIAL_STATE__;"
                ]

                for js_data_script in js_data_list:
                    script_data = self.driver.execute_script(js_data_script)
                    if script_data:
                        rating_js = script_data.get('product', {}).get('ratingScore')
                        review_count_js = script_data.get('product', {}).get('commentCount')
                        if rating_js or review_count_js:
                            final_data.update({"Rating": rating_js, "Review Count": review_count_js})
                            break
            except WebDriverException:
                final_data["DataSource"] = "JavaScript (Hata)"

            # 3. Aşama: O da başarısız olursa JSON-LD'yi dene (En yavaş yol)
            print("     -> JavaScript verisi eksik. JSON-LD deniyor...")
            final_data["DataSource"] = "JSON-LD"
            try:
                html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5).text
                soup = BeautifulSoup(html, "html.parser")
                scripts = soup.find_all("script", type="application/ld+json")
                for script in scripts:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get("@type") == "Product":
                        rating_data = data.get("aggregateRating", {})
                        final_data.update({
                            "Rating": rating_data.get("ratingValue"),
                            "Review Count": rating_data.get("reviewCount")
                        })
                        break
            except Exception as e:
                print(f"     JSON-LD verisi çekilirken hata oluştu: {e}")
                final_data["DataSource"] = "JSON-LD (Hata)"

            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            print(f"     -> İşlem tamamlandı. Kaynak: {final_data['DataSource']}. Geçen süre: {elapsed_time} saniye\n")
            return final_data

        except Exception as e:
            end_time = time.time()
            elapsed_time = round(end_time - start_time, 2)
            print(f"     -> Ürün detayı çekilirken genel hata oluştu: {e}")
            print(f"     -> İşlem hata ile tamamlandı. Geçen süre: {elapsed_time} saniye\n")
            return None