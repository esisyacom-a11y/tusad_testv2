import json
import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from fetcher import fetch_html_with_requests, fetch_html_with_selenium
"""ÜRÜN DETAYLARINI SAYFA İÇERİĞİNDEN PARSE EDER."""

def parse_product_details(driver, url):
    print(f"     -> Ürün detayları çekiliyor: {url}")
    try:
        html = fetch_html_with_requests(url)
        if not html:
            html = fetch_html_with_selenium(driver, url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # JSON-LD verisini yakala
        json_ld_data = None
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "Product":
                    json_ld_data = data
                    break
            except:
                continue

        # JSON-LD'den veri çek
        price, discount, rating, review_count = None, None, None, None
        if json_ld_data:
            offer = json_ld_data.get("offers", {})
            if offer.get("@type") == "AggregateOffer":
                price = f"{offer.get('price')} TL"
                discount = f"{offer.get('highPrice')} TL" if 'highPrice' in offer else None
            elif offer.get("@type") == "Offer":
                price = f"{offer.get('price')} TL"

            rating_data = json_ld_data.get("aggregateRating", {})
            rating = rating_data.get("ratingValue")
            review_count = rating_data.get("reviewCount")

        # Eksikse Selenium ile tamamla
        driver.get(url)

        if not price:
            try:
                price_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'prc-box-sllng')]/span | //span[contains(@class, 'prc-org')]")
                if len(price_elements) == 2:
                    price = price_elements[0].text.strip()
                    discount = price_elements[1].text.strip()
                elif len(price_elements) == 1:
                    price = price_elements[0].text.strip()
            except NoSuchElementException:
                pass

        product_name = driver.find_element(By.CSS_SELECTOR, "h1.product-title").text
        brand = driver.find_element(By.CSS_SELECTOR, "strong").text.strip()
        product_only = product_name.replace(brand, "").strip()
        seller = driver.find_element(By.CSS_SELECTOR, "div.merchant-name").text.strip()
        seller_rating = driver.find_element(By.CSS_SELECTOR, "div.score-badge").text.strip()

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