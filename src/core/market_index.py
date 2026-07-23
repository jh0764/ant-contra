import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import yfinance as yf

@st.cache_data(ttl=600, show_spinner=False)
def get_market_index_series(is_kosdaq: bool):
    # 개별 종목 가격 데이터(core.price_data)와 동일한 FDR 소스로 통일
    # → yfinance와의 거래일/휴장일 정렬 불일치로 인한 RS(상대강도) 왜곡 방지
    code = "KQ11" if is_kosdaq else "KS11"
    try:
        data = fdr.DataReader(
            code,
            start=(pd.Timestamp.now() - pd.Timedelta(days=100)).strftime("%Y-%m-%d")
        )
        if not data.empty and len(data) > 2:
            return data["Close"].dropna(), None
    except Exception as e1:  
        fdr_error = str(e1)
    else:
        fdr_error = "빈 데이터 반환"   
        
    # 2차: FDR 실패 시 yfinance 폴백 (지수 카드 자체가 비는 것 방지)
    yf_code = "^KQ11" if is_kosdaq else "^KS11"
    try:
        data = yf.download(yf_code, period="3mo", interval="1d", progress=False, auto_adjust=True)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        if not data.empty:
            return data["Close"].dropna(), None
        yf_error = "빈 데이터 반환"
    except Exception as e2:    
        yf_error = str(e2)
    return None, f"FDR: {fdr_error} / yfinance: {yf_error}"    
            
def calculate_rs_indicator(close_series, index_series, lookback=20):
    try:
        if index_series is None or len(close_series) < lookback or len(index_series) < lookback:
            raise ValueError("데이터 부족")

        stock_ret = float(close_series.iloc[-1] / close_series.iloc[-lookback] - 1)
        index_ret = float(index_series.iloc[-1] / index_series.iloc[-lookback] - 1)
        rs_diff = (stock_ret - index_ret) * 100
        market_selloff = index_ret <= -0.05

        if rs_diff <= -10:
            status, label = "green", f"시장 대비 초과하락 ({rs_diff:+.1f}%p)"
            desc = "종목 고유 악재로 저평가 가능성. 개별 역발상 신뢰도 높음" if not market_selloff \
                   else "시장 전체 급락 동반 초과하락 — 종목 고유 원인인지 재확인 필요"
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

        return {"status": status, "label": label, "desc": desc, "score": score, "value": rs_diff}
    except Exception:
        return {"status": "yellow", "label": "RS — 계산 불가", "desc": "지수 데이터 부족", "score": 0, "value": None}