import streamlit as st
import pandas as pd
from core.price_data import load_price_data
from core.indicators import calculate_objective_indicators

KOSPI_UNIVERSE = [
    "005930", "000660", "035420", "035720", "373220", "207940", "005380",
    "000270", "068270", "005490", "051910", "006400", "012330", "105560",
    "055550", "028260", "012450", "034020", "032830", "066570", "003670",
    "017670", "015760", "096770", "010130", "011200", "086790", "024110",
    "009150", "047810",
]

# 코스닥 대형주 (2026년 상반기 기준, 순위 변동이 잦으니 주기적으로 점검 권장)
KOSDAQ_UNIVERSE = [
    "086520", "196170", "247540", "263750", "293490",
    "058470", "214150", "214450", "000250", "141080",
]

def _scan_universe(codes, is_kosdaq):
    results = []
    for code in codes:
        try:
            df, _suffix = load_price_data(code)
            if df is None or df.empty or len(df) < 30:
                continue
            df = df.reset_index()
            close = df['Close'].squeeze()
            volume = df['Volume'].squeeze() if 'Volume' in df.columns else pd.Series(dtype=float)
            high = df['High'].squeeze() if 'High' in df.columns else None
            low = df['Low'].squeeze() if 'Low' in df.columns else None
            open_s = df['Open'].squeeze() if 'Open' in df.columns else None

            _, objective_score = calculate_objective_indicators(
                close, volume, {"error": "scan_skip"}, {"error": "scan_skip"},
                is_kosdaq, high, low, open_series=open_s
            )
            current_price = int(close.iloc[-1])
            prev_price = int(close.iloc[-2])
            change_pct = round((current_price - prev_price) / prev_price * 100, 2)

            results.append({
                "code": code, "score": objective_score,
                "price": current_price, "change_pct": change_pct,
            })
        except Exception:
            continue

    results.sort(key=lambda r: (r["score"], abs(r["change_pct"])), reverse=True)
    return results

@st.cache_data(ttl=3600, show_spinner=False)
def run_fear_scanner(top_n=10):
    return {
        "kospi": _scan_universe(KOSPI_UNIVERSE, is_kosdaq=False)[:top_n],
        "kosdaq": _scan_universe(KOSDAQ_UNIVERSE, is_kosdaq=True)[:top_n],
    }