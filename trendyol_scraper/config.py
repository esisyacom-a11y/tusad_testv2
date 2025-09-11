# trendyol_scraper/config.py
import os

# Sabit Değerler
TIMEOUT = 30
MAX_RETRY = 3
RETRY_WAIT = 5
PRODUCT_LIMIT_PER_SEARCH = 5

# URL'ler
BASE_URL = "https://www.trendyol.com"
SEARCH_URL = "https://www.trendyol.com/sr?q={}"

# Klasör ve dosya isimleri
MAIN_FOLDER = "Trendyol_Urunler"
EXCEL_FILE_PATH = r"C:\Users\esisy\Downloads\Başlıksız e-tablo (2).xlsx"

# Seçiciler (Selectors)
COOKIE_ACCEPT_BUTTON_ID = 'onetrust-accept-btn-handler'
PRODUCT_CONTAINER_CSS = "div.prdct-cntnr-wrppr"
PRODUCT_CARD_CSS = "div.p-card-wrppr"
PRODUCT_LINK_CLASS = "p-card-chldrn-cntnr"
PRODUCT_IMAGE_TAG = "img"
PRODUCT_TITLE_CSS = "h1.product-title"
BRAND_NAME_CSS = "strong"
SELLER_NAME_CSS = "div.merchant-name"
SELLER_RATING_CSS = "div.score-badge"