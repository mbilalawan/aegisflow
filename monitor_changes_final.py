import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import subprocess
import pandas as pd
from datetime import datetime

SCRAPER_SCRIPT = "Scrapper_final.py"
REPAIR_SCRIPT = "Repair_Agent.py"
FRAGILE_CSV = "fragile_results.csv"
CHANGE_LOG = "change_history.csv"
METRICS_CSV = "system_metrics.csv"

def log_event(event_type, status, details=""):
    file_exists = os.path.isfile(METRICS_CSV)
    with open(METRICS_CSV, "a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Event_Type", "Status", "Details"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event_type, status, details])

def log_drift(category, element, new_val):
    file_exists = os.path.isfile(CHANGE_LOG)
    session_id = f"SESS-{datetime.now().strftime('%M%S')}"
    with open(CHANGE_LOG, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Session_ID", "Timestamp", "Category", "Element", "Property", "Old_Value", "New_Value"])
        writer.writerow([session_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), category, element, "Value", "unknown", new_val])

def analyze_drift():
    print("🔎 Analyzing website for changes...")
    try:
        # Check HTML
        res = requests.get("http://localhost:5000", timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        t_el = soup.find(attrs={"data-field": "title"})
        if t_el: log_drift("CSS Rename", "Title", t_el.get('class')[0])
        p_el = soup.find(attrs={"data-field": "price"})
        if p_el: log_drift("CSS Rename", "Price", p_el.get('class')[0])

        # Check API status
        res_api = requests.get("http://localhost:5000/api/status", timeout=5)
        status = res_api.json()
        if status.get('unit_version', 1) > 1:
            log_drift("Unit Drift", "Price", "Numeric_Fix")
        if status.get('json_version', 1) > 1:
            log_drift("JSON Nesting", "API", status['json_version'])
    except Exception as e:
        print(f"[-] Analysis Error: {e}")

def main():
    while True:
        print(f"\n--- Cycle Start: {datetime.now().strftime('%H:%M:%S')} ---")
        subprocess.run(["python", SCRAPER_SCRIPT])
        
        if os.path.exists(FRAGILE_CSV):
            df = pd.read_csv(FRAGILE_CSV)
            if not df.empty:
                last_status = df.iloc[-1]['Run_Status']
                log_event("Scrape_Attempt", last_status)
                
                if last_status == "Failed":
                    print("🚨 Scraper Failed! Triggering Repair...")
                    analyze_drift()
                    subprocess.run(["python", REPAIR_SCRIPT])
                else:
                    print("✅ Scrape Success.")
        
        time.sleep(15)

if __name__ == "__main__":
    main()