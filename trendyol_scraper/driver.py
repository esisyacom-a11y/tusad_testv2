# trendyol_scraper/driver.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .config import COOKIE_ACCEPT_BUTTON_ID

class WebDriverManager:
    """Selenium WebDriver'ı yönetir."""

    def __init__(self):
        self.driver = None

    def get_driver(self):
        """Chrome sürücüsünü başlatır veya mevcut sürücüyü döndürür."""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return self.driver

    def quit_driver(self):
        """Sürücüyü kapatır."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def accept_cookies(self):
        """Çerezleri kabul eder."""
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, COOKIE_ACCEPT_BUTTON_ID))
            ).click()
            print("Çerezler kabul edildi.")
        except:
            print("Çerez butonu bulunamadı veya tıklanamadı.")
            pass