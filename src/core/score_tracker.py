import json
import os
from datetime import date

# 프로젝트 루트 기준 절대경로 (배포 환경에서 cwd가 달라져도 안전)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HISTORY_PATH = os.path.join(_BASE_DIR, "data", "score_history.json")


def _load_history():
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_history(history):
    try:
        os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f)
    except OSError:
        # 배포 환경의 파일시스템이 읽기 전용/ephemeral이어도 앱이 죽지 않도록 방어
        pass


def record_and_get_delta(ticker_code, current_score):
    today = date.today().isoformat()
    history = _load_history()
    entry = history.get(ticker_code)
    delta = (current_score - entry["score"]) if entry else None
    if entry is None or entry["date"] != today:
        history[ticker_code] = {"score": current_score, "date": today}
        _save_history(history)
    return delta