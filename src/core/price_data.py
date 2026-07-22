import streamlit as st
import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr

@st.cache_data(ttl=60 * 10, show_spinner=False)
def load_price_data(ticker_code: str):
    # 1차: FinanceDataReader (국내 거래소 데이터, 배당/분할 조정 오류 이슈 없음)
    try:
        fdr_data = fdr.DataReader(
            ticker_code,
            start=(pd.Timestamp.now() - pd.Timedelta(days=365)).strftime("%Y-%m-%d")
        )
        if not fdr_data.empty and len(fdr_data) > 20:
            fdr_data.index = pd.to_datetime(fdr_data.index).tz_localize(None)
            return fdr_data, None
    except Exception:
        pass

    # 2차: yfinance 백업 (fdr 실패 시에만)
    result_data = pd.DataFrame()
    result_suffix = None
    for suffix in [".KS", ".KQ"]:
        try:
            data = yf.download(
                f"{ticker_code}{suffix}",
                period="1y",
                interval="1d",
                progress=False,
                auto_adjust=True,
            )
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                result_data = data
                result_suffix = suffix
                break
        except Exception:
            continue

    if not result_data.empty and "Close" in result_data.columns:
        result_data = result_data.dropna(subset=["Close"])

    return result_data, result_suffix
