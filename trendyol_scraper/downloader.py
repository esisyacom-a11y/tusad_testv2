import requests
import time
import os
from .config import TIMEOUT, MAX_RETRY, RETRY_WAIT


class ImageDownloader:

    def __init__(self, timeout=TIMEOUT, max_retry=MAX_RETRY, retry_wait=RETRY_WAIT):
        self.timeout = timeout
        self.max_retry = max_retry
        self.retry_wait = retry_wait

    def download(self, thumbnails, save_folder, urun_id):
        if not thumbnails:
            print(f" {urun_id} için uygun görsel bulunamadı.")
            return 0

        os.makedirs(save_folder, exist_ok=True)
        count = 0

        # Sık kullanılan resim türlerini dosya uzantılarına eşleyen sözlük
        content_type_to_ext = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg'
        }

        for i, img_tag in enumerate(thumbnails):
            img_url = img_tag.get("src")
            if not img_url:
                continue

            ext = None

            print(f"    {urun_id}_{i + 1} için {img_url} indiriliyor...")

            for attempt in range(1, self.max_retry + 1):
                try:
                    response = requests.get(img_url, timeout=self.timeout)
                    response.raise_for_status()  # Hatalı HTTP durum kodları için hata fırlatır

                    content_type = response.headers.get('Content-Type')
                    if content_type in content_type_to_ext:
                        ext = content_type_to_ext[content_type]
                    else:
                        ext = os.path.splitext(img_url)[1].split("?")[0]
                        if not ext:
                            ext = '.jpg'  # Varsayılan uzantı

                    filename = f"{urun_id}_{i + 1}{ext}"
                    save_path = os.path.join(save_folder, filename)

                    with open(save_path, "wb") as f:
                        f.write(response.content)

                    count += 1
                    print(f"    {filename} başarıyla indirildi.")
                    break

                except requests.exceptions.RequestException as e:
                    print(f"    Hata ({attempt}. deneme): {e}")
                except Exception as e:
                    print(f"    Beklenmedik bir hata oluştu: {e}")

                if attempt < self.max_retry:
                    time.sleep(self.retry_wait)
            else:
                print("    Maksimum deneme sayısına ulaşıldı, resim atlandı.")

        return count