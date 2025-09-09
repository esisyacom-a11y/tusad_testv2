# trendyol_scraper/fetcher.py
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from .config import PRODUCT_CONTAINER_CSS, PRODUCT_CARD_CSS, TIMEOUT

class PageFetcher:
    """Sayfa içeriği çekme işlemlerini yönetir."""

    def __init__(self, driver):
        self.driver = driver

    def get_dynamic_page(self, url):
        """Selenium kullanarak dinamik sayfayı çeker."""
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_CONTAINER_CSS))
            )
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_CARD_CSS))
            )
            return self.driver.page_source
        except TimeoutException:
            print(f"  Sayfa yüklenemedi: {url}")
            return None

    def get_static_page(self, url):
        """Requests kullanarak statik bir sayfanın HTML'ini çeker."""
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            return response.text
        except Exception as e:
            print(f"   Statik sayfa çekilirken hata oluştu: {e}")
            return None