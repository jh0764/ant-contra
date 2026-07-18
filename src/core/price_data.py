import streamlit as st
import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr

# Download Price Data (KOSPI vs KOSDAQ Suffix Handling)
@st.cache_data(ttl=60 * 10, show_spinner=False)
def load_price_data(ticker_code: str):
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
                # MultiIndex 컬럼 평탄화 (yfinance 최신 버전 대응)
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                result_data = data
                result_suffix = suffix
                break
        except Exception:
            continue

    # 당일 데이터 누락 시 fdr로 보완
    if not result_data.empty:
            last_date = result_data.index[-1].date()
            today = pd.Timestamp.now().date()
            if last_date < today:
                try:
                    fdr_supplement = fdr.DataReader(
                        ticker_code,
                        start=(pd.Timestamp.now() - pd.Timedelta(days=365)).strftime("%Y-%m-%d")
                    )
                    if not fdr_supplement.empty:
                        # 인덱스 timezone 제거하여 비교 정합성 확보
                        if isinstance(result_data.columns, pd.MultiIndex):
                            result_data.columns = result_data.columns.get_level_values(0)
                        result_data.index = pd.to_datetime(result_data.index).tz_localize(None)

                        result_data.index = pd.to_datetime(result_data.index).tz_localize(None)
                        fdr_supplement.index = pd.to_datetime(fdr_supplement.index).tz_localize(None)

                        fdr_supplement = fdr_supplement[~fdr_supplement.index.isin(result_data.index)]
                        # 컬럼 구조 일치시키기 (yfinance: Open/High/Low/Close/Volume)
                        needed_cols = ["Open", "High", "Low", "Close", "Volume"]
                        common_cols = [c for c in needed_cols if c in result_data.columns and c in fdr_supplement.columns]

                        if not fdr_supplement.empty and len(common_cols) >= 4:
                            fdr_supplement = fdr_supplement[common_cols]
                            result_data = result_data[common_cols]
                            result_data = pd.concat([result_data, fdr_supplement])
                            result_data = result_data.sort_index()
                except Exception:
                    pass

    # 최종 안전장치: NaN 행 제거
    if not result_data.empty:
        if isinstance(result_data.columns, pd.MultiIndex):
            result_data.columns = result_data.columns.get_level_values(0)
        if "Close" in result_data.columns:
            result_data = result_data.dropna(subset=["Close"])
    else:
        # yfinance 완전 실패 시 fdr 단독 사용
        try:
            fdr_data = fdr.DataReader(ticker_code, start=(pd.Timestamp.now() - pd.Timedelta(days=365)))
            if not fdr_data.empty:
                result_data = fdr_data
                result_suffix = ".KQ"  # fdr만 성공한 경우 임시값, 아래 로직에서 보정 필요
        except Exception:
            pass

# 첫 봉이 다음 봉 대비 상하한가(±30%) 초과 시 캐시 오염 의심 → 원본 반환하지 않고 결측 처리
    if not result_data.empty and len(result_data) >= 2 and "Close" in result_data.columns:
        c0, c1 = result_data["Close"].iloc[0], result_data["Close"].iloc[1]
        if c1 > 0 and abs(c0 - c1) / c1 > 0.30:
            result_data = result_data.iloc[1:]  # 의심 행만 제거, 나머지는 그대로 사용

    return result_data, result_suffix
