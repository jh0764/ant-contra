import json
import os
from datetime import date

HISTORY_PATH = os.path.join("data", "score_history.json")

def _load_history():
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_history(history):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f)

def record_and_get_delta(ticker_code, current_score):
    today = date.today().isoformat()
    history = _load_history()
    entry = history.get(ticker_code)
    delta = (current_score - entry["score"]) if entry else None
    if entry is None or entry["date"] != today:
        history[ticker_code] = {"score": current_score, "date": today}
        _save_history(history)
    return delta