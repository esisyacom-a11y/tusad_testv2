import requests
import time
import os
from .config import TIMEOUT, MAX_RETRY, RETRY_WAIT

class ImageDownloader:
    """Ürün detay sayfasındaki tüm thumbnail görselleri indirir."""

    def __init__(self, timeout=TIMEOUT, max_retry=MAX_RETRY, retry_wait=RETRY_WAIT):
        self.timeout = timeout
        self.max_retry = max_retry
        self.retry_wait = retry_wait

    def download(self, thumbnails, save_folder, urun_id):
        if not thumbnails:
            print(f"⚠️ {urun_id} için uygun görsel bulunamadı.")
            return 0

        os.makedirs(save_folder, exist_ok=True)
        count = 0

        for i, img_tag in enumerate(thumbnails):
            img_url = img_tag.get("src")
            if not img_url:
                continue

            ext = os.path.splitext(img_url)[1].split("?")[0]
            if not ext:
                ext = ".jpg"

            filename = f"{urun_id}_{i+1}{ext}"
            save_path = os.path.join(save_folder, filename)

            print(f"   ⬇️ {filename} indiriliyor...")

            for attempt in range(1, self.max_retry + 1):
                try:
                    img_data = requests.get(img_url, timeout=self.timeout).content
                    with open(save_path, "wb") as f:
                        f.write(img_data)
                    count += 1
                    break
                except requests.exceptions.ReadTimeout:
                    print(f"   ReadTimeout, {attempt}. deneme")
                except requests.exceptions.ConnectTimeout:
                    print(f"   ConnectTimeout, {attempt}. deneme")
                except Exception as e:
                    print(f"   Resim indirilemedi: {e}")

                if attempt < self.max_retry:
                    time.sleep(self.retry_wait)
            else:
                print("   Maksimum deneme sayısına ulaşıldı, resim atlandı.")

        return count
