import pandas as pd
import streamlit as st
import FinanceDataReader as fdr
from core.indicators import calculate_objective_indicators
from core.scanner import KOSPI_UNIVERSE, KOSDAQ_UNIVERSE

FORWARD_WINDOWS = [5, 10, 20]
SCORE_BUCKETS = [(0, 35), (35, 55), (55, 70), (70, 85), (85, 101)]
MIN_HISTORY = 210  # 200일선 계산에 필요한 최소 관측치 + 여유분
BACKTEST_YEARS = 3  # 대시보드용 1년 로더와 별개로, 여러 시장 국면을 포괄하기 위해 장기 로드


@st.cache_data(ttl=3600 * 12, show_spinner=False)
def _load_backtest_price(ticker_code):
    try:
        start = (pd.Timestamp.now() - pd.Timedelta(days=365 * BACKTEST_YEARS)).strftime("%Y-%m-%d")
        data = fdr.DataReader(ticker_code, start=start)
        if data.empty or len(data) < MIN_HISTORY + max(FORWARD_WINDOWS) + 1:
            return None
        return data.reset_index()
    except Exception:
        return None


def _run_single_ticker(ticker_code, is_kosdaq):
    """
    한 종목에 대해 과거 매 거래일 t 시점까지의 데이터만으로 objective_score를 재계산하고,
    t+5/10/20일 뒤 실제 수익률과 짝지어 기록. (미래 데이터 유출 방지)
    """
    df = _load_backtest_price(ticker_code)
    if df is None:
        return pd.DataFrame()

    close = df['Close']
    volume = df['Volume'] if 'Volume' in df.columns else pd.Series(dtype=float, index=df.index)
    high = df['High'] if 'High' in df.columns else None
    low = df['Low'] if 'Low' in df.columns else None
    open_col = df['Open'] if 'Open' in df.columns else None

    last_valid_idx = len(df) - max(FORWARD_WINDOWS) - 1
    records = []

    for t in range(MIN_HISTORY, last_valid_idx):
        try:
            c_slice = close.iloc[:t + 1]
            v_slice = volume.iloc[:t + 1]
            h_slice = high.iloc[:t + 1] if high is not None else None
            l_slice = low.iloc[:t + 1] if low is not None else None
            o_slice = open_col.iloc[:t + 1] if open_col is not None else None

            # 커뮤니티/외국인/뉴스 데이터는 과거 시점 재현 불가 → objective_score만 검증 대상
            _, score = calculate_objective_indicators(
                c_slice, v_slice, {"error": "backtest_skip"}, {"error": "backtest_skip"},
                is_kosdaq, h_slice, l_slice, open_series=o_slice
            )
            entry_price = float(close.iloc[t])
            row = {"code": ticker_code, "score": score}
            for w in FORWARD_WINDOWS:
                fwd_price = float(close.iloc[t + w])
                row[f"fwd_{w}d"] = (fwd_price - entry_price) / entry_price * 100
            records.append(row)
        except Exception:
            continue

    return pd.DataFrame(records)


@st.cache_data(ttl=3600 * 6, show_spinner=False)
def run_universe_backtest(max_tickers=None):
    """
    KOSPI_UNIVERSE + KOSDAQ_UNIVERSE 전 종목을 대상으로 백테스트를 돌려 합산.
    max_tickers로 표본 수를 줄여 속도 조절 가능 (None이면 전체).
    """
    universe = [(c, False) for c in KOSPI_UNIVERSE] + [(c, True) for c in KOSDAQ_UNIVERSE]
    if max_tickers:
        universe = universe[:max_tickers]

    all_records = []
    for code, is_kosdaq in universe:
        result = _run_single_ticker(code, is_kosdaq)
        if not result.empty:
            all_records.append(result)

    if not all_records:
        return pd.DataFrame()
    return pd.concat(all_records, ignore_index=True)


def summarize_backtest(df):
    """점수 구간별 평균 수익률 + 승률(양의 수익률 비율) 집계. 표본 0건 구간도 항상 포함."""
    if df is None or df.empty:
        return pd.DataFrame()

    rows = []
    for lo, hi in SCORE_BUCKETS:
        bucket = df[(df["score"] >= lo) & (df["score"] < hi)]
        if bucket.empty:
            continue
        row = {"점수구간": f"{lo}~{hi - 1}점", "표본수": len(bucket)}
        for w in FORWARD_WINDOWS:
            col = f"fwd_{w}d"
            row[f"{w}일 평균수익률(%)"] = round(bucket[col].mean(), 2)
            row[f"{w}일 승률(%)"] = round((bucket[col] > 0).mean() * 100, 1)
        rows.append(row)

    return pd.DataFrame(rows)


def get_baseline_returns(df):
    """점수와 무관하게 유니버스 전체를 그냥 들고 있었을 때 평균 수익률 (비교 기준선)."""
    if df is None or df.empty:
        return {w: 0.0 for w in FORWARD_WINDOWS}
    return {w: round(df[f"fwd_{w}d"].mean(), 2) for w in FORWARD_WINDOWS}