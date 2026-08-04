import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import yfinance as yf


@st.cache_data(ttl=600, show_spinner=False)
def get_market_index_series(is_kosdaq: bool):
    code = "KQ11" if is_kosdaq else "KS11"
    fdr_error = None

    # 1차: FinanceDataReader 수집
    try:
        data = fdr.DataReader(
            code,
            start=(pd.Timestamp.now() - pd.Timedelta(days=100)).strftime("%Y-%m-%d"),
        )
        if not data.empty and len(data) > 2:
            close_s = data["Close"].squeeze()
            if isinstance(close_s, pd.DataFrame):
                close_s = close_s.iloc[:, 0]
            if isinstance(close_s, pd.Series) and not close_s.empty:
                return close_s.dropna(), None
        fdr_error = "데이터 없음 또는 구조 불일치"
    except Exception as e1:
        fdr_error = str(e1)

    # 2차: yfinance 폴백
    yf_code = "^KQ11" if is_kosdaq else "^KS11"
    try:
        data = yf.download(
            yf_code, period="3mo", interval="1d", progress=False, auto_adjust=True
        )
        if not data.empty and "Close" in data.columns:
            close_s = data["Close"].squeeze()
            if isinstance(close_s, pd.DataFrame):
                close_s = close_s.iloc[:, 0]
            if isinstance(close_s, pd.Series) and not close_s.empty:
                return close_s.dropna(), None
        yf_error = "빈 데이터 반환"
    except Exception as e2:
        yf_error = str(e2)

    return None, f"FDR: {fdr_error} / yfinance: {yf_error}"


def calculate_rs_indicator(close_series, index_series, lookback=20):
    try:
        if index_series is None or close_series is None:
            raise ValueError("지수 또는 종목 데이터가 None입니다.")

        # DataFrame으로 들어올 경우 1차원 Series로 강제 변환
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.squeeze()
        if isinstance(index_series, pd.DataFrame):
            index_series = index_series.squeeze()

        if len(close_series) < lookback or len(index_series) < lookback:
            raise ValueError(f"데이터 부족 (종목:{len(close_series)}, 지수:{len(index_series)})")

        stock_ret = (
            float(close_series.iloc[-1]) / float(close_series.iloc[-lookback]) - 1
        )
        index_ret = (
            float(index_series.iloc[-1]) / float(index_series.iloc[-lookback]) - 1
        )
        rs_diff = (stock_ret - index_ret) * 100
        market_selloff = index_ret <= -0.05

        if rs_diff <= -10:
            status, label = "green", f"시장 대비 초과하락 ({rs_diff:+.1f}%p)"
            desc = (
                "종목 고유 악재로 저평가 가능성. 개별 역발상 신뢰도 높음"
                if not market_selloff
                else "시장 전체 급락 동반 초과하락 — 종목 고유 원인인지 재확인 필요"
            )
            score = 8 if not market_selloff else 3
        elif rs_diff <= 0:
            status, label = "yellow", f"시장 대비 소폭 부진 ({rs_diff:+.1f}%p)"
            desc, score = "시장과 유사한 흐름. 특이 신호 아님", 1
        elif rs_diff <= 10:
            status, label = "yellow", f"시장 대비 소폭 우위 ({rs_diff:+.1f}%p)"
            desc, score = "시장 대비 견조. 공포 국면 아닐 가능성", -2
        else:
            status, label = "red", f"시장 대비 초과상승 ({rs_diff:+.1f}%p)"
            desc, score = "이미 시장 대비 강세. 역발상 매수 시점 아님", -6

        return {
            "status": status,
            "label": label,
            "desc": desc,
            "score": score,
            "value": rs_diff,
        }
    except Exception as e:
        return {
            "status": "yellow",
            "label": f"RS — 계산 불가 ({e})",
            "desc": "지수 데이터 확인 필요",
            "score": 0,
            "value": None,
        }


def get_usdkrw_data():
    try:
        ticker = yf.Ticker("KRW=X")
        # 1개월 환율 데이터 수집
        df = ticker.history(period="1mo")
        if df.empty or len(df) < 2:
            return None

        close_series = df["Close"]
        current = float(close_series.iloc[-1])
        prev = float(close_series.iloc[-2])
        change_pct = (current - prev) / prev * 100

        return {"current": current, "change_pct": change_pct, "series": close_series}
    except Exception:
        return None
