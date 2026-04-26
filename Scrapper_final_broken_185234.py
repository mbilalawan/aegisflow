import requests
from bs4 import BeautifulSoup
import json, csv, os
from datetime import datetime

# AegisFlow Version: 36
URL = "http://localhost:5000"
DATA_FILE = "fragile_results.csv"

def save_to_csv(ts, title, price, status):
    fieldnames = ["Timestamp", "Title", "Price", "Run_Status"]
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not os.path.isfile(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
            writer.writeheader()
        writer.writerow({"Timestamp": ts, "Title": title, "Price": price, "Run_Status": status})

def run_extraction():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    kb = {'product_title': {'class': 'product-title'}, 'price_value': {'class': 'price-color'}, 'patch_version': 36, 'unit_drift_active': True, 'last_session_repaired': 'SESS-5211'}
    try:
        res = requests.get(URL, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        title_el = soup.find(class_=kb['product_title']['class'])
        price_el = soup.find(class_=kb['price_value']['class'])
        title = title_el.text.strip() if title_el else "N/A"
        price_raw = price_el.text.strip() if price_el else "N/A"
        
        if kb.get('unit_drift_active'):
            price_final = "".join(c for c in price_raw if c.isdigit() or c == '.')
        else:
            price_final = price_raw if price_raw.startswith('$') else "N/A"

        if price_final == "N/A" or title == "N/A":
            save_to_csv(timestamp, title, price_raw, "Failed")
        else:
            save_to_csv(timestamp, title, price_final, "Success")
            print(f"[+] Scraped v{kb['patch_version']}: {title} | {price_final}")
    except:
        save_to_csv(timestamp, "N/A", "N/A", "Failed")

if __name__ == "__main__":
    run_extraction()
