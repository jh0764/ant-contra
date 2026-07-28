import json
import os
from datetime import date

# 프로젝트 루트 기준 절대경로 (배포 환경에서 cwd가 달라져도 안전)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HISTORY_PATH = os.path.join(_BASE_DIR, "data", "score_history.json")

MAX_KEEP = 180  # 종목당 최근 180영업일(약 8~9개월)치만 보관, 파일 무한 증식 방지


def _load_history():
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

    # 구버전 포맷({"code": {"score":X,"date":Y}}) → 신버전 리스트 포맷 자동 마이그레이션
    migrated = {}
    for code, entry in raw.items():
        if isinstance(entry, list):
            migrated[code] = entry
        elif isinstance(entry, dict):
            migrated[code] = [entry]
    return migrated


def _save_history(history):
    try:
        os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False)
    except OSError:
        # 배포 환경의 파일시스템이 읽기 전용/ephemeral이어도 앱이 죽지 않도록 방어
        pass


def record_and_get_delta(ticker_code, current_score):
    today = date.today().isoformat()
    history = _load_history()
    series = history.get(ticker_code, [])

    delta = (current_score - series[-1]["score"]) if series else None

    if not series or series[-1]["date"] != today:
        series = series + [{"score": current_score, "date": today}]
        series = series[-MAX_KEEP:]
        history[ticker_code] = series
        _save_history(history)

    return delta


def get_score_history(ticker_code, days=60):
    """최근 N영업일 점수 시계열 반환 (스파크라인용). [{"score":.., "date":..}, ...]"""
    history = _load_history()
    series = history.get(ticker_code, [])
    return series[-days:]