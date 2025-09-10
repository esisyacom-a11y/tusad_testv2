# utils.py
import requests

def get_usd_exchange_rate():
    try:
        response = requests.get("http://hasanadiguzel.com.tr/api/kurgetir")
        data = response.json()
        for item in data["TCMB_AnlikKurBilgileri"]:
            if item["CurrencyName"] == "US DOLLAR":
                return float(item["ForexSelling"])
    except Exception as e:
        print(f"Döviz kuru alınırken hata oluştu: {e}")
        return None