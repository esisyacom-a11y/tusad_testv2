# trendyol_scraper/downloader.py
import requests
import time
import os
from .config import TIMEOUT, MAX_RETRY, RETRY_WAIT

class ImageDownloader:
    """Resim indirme işlemini yönetir."""

    def __init__(self, timeout=TIMEOUT, max_retry=MAX_RETRY, retry_wait=RETRY_WAIT):
        self.timeout = timeout
        self.max_retry = max_retry
        self.retry_wait = retry_wait

    def download(self, img_url, save_path):
        for attempt in range(1, self.max_retry + 1):
            try:
                img_data = requests.get(img_url, timeout=self.timeout).content
                with open(save_path, "wb") as f:
                    f.write(img_data)
                return True
            except requests.exceptions.ReadTimeout:
                print(f"   ReadTimeout, {attempt}. deneme")
            except requests.exceptions.ConnectTimeout:
                print(f"   ConnectTimeout, {attempt}. deneme")
            except Exception as e:
                print(f"   Resim indirilemedi: {e}")

            if attempt < self.max_retry:
                time.sleep(self.retry_wait)
        print("   Maksimum deneme sayısına ulaşıldı, resim atlandı.")
        return False