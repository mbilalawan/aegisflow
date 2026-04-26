import pandas as pd
import json
import os
import time
import csv
import shutil
from datetime import datetime

# --- CONFIGURATION ---
CHANGE_LOG = "change_history.csv"
SELECTOR_KB = "active_selectors.json"
TARGET_SCRAPER = "Scrapper_final.py"
HISTORY_FOLDER = "repair_history" # New folder for your paper's data
METRICS_CSV = "system_metrics.csv"

# Ensure history folder exists
if not os.path.exists(HISTORY_FOLDER):
    os.makedirs(HISTORY_FOLDER)

def log_event(event_type, status, details=""):
    file_exists = os.path.isfile(METRICS_CSV)
    with open(METRICS_CSV, "a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Event_Type", "Status", "Details"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event_type, status, details])

def generate_healed_scraper_code(version, kb):
    """Synthesizes the scraper code using repr() for Python-safe booleans."""
    return f"""import requests
from bs4 import BeautifulSoup
import json, csv, os
from datetime import datetime

# AegisFlow Version: {version}
URL = "http://localhost:5000"
DATA_FILE = "fragile_results.csv"

def save_to_csv(ts, title, price, status):
    fieldnames = ["Timestamp", "Title", "Price", "Run_Status"]
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not os.path.isfile(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
            writer.writeheader()
        writer.writerow({{"Timestamp": ts, "Title": title, "Price": price, "Run_Status": status}})

def run_extraction():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    kb = {repr(kb)}
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
            print(f"[+] Scraped v{{kb['patch_version']}}: {{title}} | {{price_final}}")
    except:
        save_to_csv(timestamp, "N/A", "N/A", "Failed")

if __name__ == "__main__":
    run_extraction()
"""

def orchestrate_repair():
    if not os.path.exists(CHANGE_LOG): return
    df = pd.read_csv(CHANGE_LOG)
    
    if os.path.exists(SELECTOR_KB):
        with open(SELECTOR_KB, 'r') as f: kb = json.load(f)
    else:
        kb = {"product_title": {"class": "product-title"}, "price_value": {"class": "price-color"}, "patch_version": 0}

    latest_session = df['Session_ID'].iloc[-1]
    if kb.get("last_session_repaired") == latest_session: return

    # 1. Update Knowledge Base
    session_changes = df[df['Session_ID'] == latest_session].to_dict('records')
    for c in session_changes:
        if c['Category'] == "CSS Rename":
            key = "product_title" if "Title" in c['Element'] else "price_value"
            kb[key]["class"] = c['New_Value']
        elif c['Category'] == "Unit Drift":
            kb["unit_drift_active"] = True

    kb["patch_version"] += 1
    kb["last_session_repaired"] = latest_session
    new_code = generate_healed_scraper_code(kb["patch_version"], kb)

    # 2. ARCHIVE LOGIC: Backup the broken file before overwriting
    if os.path.exists(TARGET_SCRAPER):
        ts = datetime.now().strftime('%H%M%S')
        broken_backup = f"Scrapper_final_broken_{ts}.py"
        os.rename(TARGET_SCRAPER, broken_backup)
        # Also move it to the history folder
        shutil.copy(broken_backup, os.path.join(HISTORY_FOLDER, broken_backup))
        print(f"📦 Archived broken version to {broken_backup}")

    # 3. Write the new working scraper
    with open(TARGET_SCRAPER, "w", encoding='utf-8') as f:
        f.write(new_code)
    
    # 4. Save a permanent record for the paper
    history_file = f"Scrapper_v{kb['patch_version']}.py"
    with open(os.path.join(HISTORY_FOLDER, history_file), "w", encoding='utf-8') as f:
        f.write(new_code)

    with open(SELECTOR_KB, 'w') as f:
        json.dump(kb, f, indent=4)
    
    # In Repair_Agent.py, update the orchestrate_repair function:
    start_time = time.time()
    # ... (perform repair) ...
    latency = time.time() - start_time

    # When logging, add the latency to the Details column
    log_event("Repair_Action", "Success", f"Latency:{latency:.2f}s | Version:v{kb['patch_version']}")
    
    print(f">> Integrated Patch v{kb['patch_version']}")

if __name__ == "__main__":
    orchestrate_repair()