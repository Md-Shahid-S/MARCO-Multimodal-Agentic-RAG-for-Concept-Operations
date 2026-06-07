# ingestion/state.py
import os, json
from datetime import datetime

STATE_FILE = "ingestion/state.json"

def get_last_ingestion_date() -> str:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
                return data.get("last_date", "2025-06-01") # Default baseline date
        except:
            pass
    return "2025-06-01"

def set_last_ingestion_date() -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    with open(STATE_FILE, "w") as f:
        json.dump({"last_date": today}, f)
