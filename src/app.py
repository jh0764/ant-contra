import streamlit as st
import pandas as pd
import numpy as np

from core.krx_listing import load_krx_listing, search_companies
from core.price_data import load_price_data
from core.naver_scraper import get_naver_discussion_by_likes, get_foreign_net_buying, get_news_vacuum
from core.sentiment import analyze_combined_sentiment
from core.indicators import calculate_objective_indicators
from core.scoring import calculate_fomo_index, calculate_final_score, get_entry_signal
from core.price_levels import calc_vwap_refund_line, calc_fibonacci_nearest
from core.fundamentals import get_fundamental_data

from ui.landing import render_landing
from ui.chart import render_stock_chart, render_candle_chart 
from ui.main_panel import render_price_info, render_community_tab, render_fundamental_stats
from ui.sidebar_cards import (
    render_entry_card, render_gauge_and_tier, render_score_metrics,
    render_signal_summary, render_fomo_panel, render_indicator_group
)
from ui.ticker_badge import render_company_header

from constants import THEME, ACCENT
from streamlit_searchbox import st_searchbox

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="개미반대로 (Ant-Contra)")
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
html, body, [class*="css"] { font-family: 'Pretendard', -apple-system, sans-serif; }
.stApp {{ background-color: {THEME['bg']}; }}
div[data-baseweb="tab-list"] {{
    gap:6px; background:{THEME['border']}; padding:5px; border-radius:12px;
    width:fit-content; margin-bottom:10px;
}}
button[data-baseweb="tab"] {{
    border-radius:9px; padding:8px 18px; color:{THEME['text_sub']};
    font-weight:600; font-size:13.5px; transition:0.15s;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    background:{THEME['surface']}; color:{ACCENT};
    box-shadow:0 1px 3px rgba(0,0,0,0.12);
}}
div[data-baseweb="tab-highlight"] {{ display:none; }}
div[data-baseweb="tab-border"] {{ display:none; }}
""", unsafe_allow_html=True)
st.markdown(f"""
<div style="font-size:22px; font-weight:800; color:{THEME['text_main']};">개미반대로</div>
<div style="font-size:12.5px; color:{THEME['text_sub']}; margin-bottom:16px;">네이버 실시간 추천 인기글 기반 역발상 스캐너</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
div[data-testid="stPlotlyChart"] {{
    border:1px solid {THEME['border']}; border-radius:14px;
    padding:12px; background:{THEME['bg']};
}}
</style>
""", unsafe_allow_html=True)



KRX_LISTING, KRX_SOURCE, KRX_ERROR = load_krx_listing()

if KRX_SOURCE == "backup":
    st.warning(
        f"⚠️ 전체 종목 리스트를 불러오지 못해 주요 종목 {len(KRX_LISTING)}개만 검색 가능한 상태입니다. "
        "잠시 후 새로고침하면 정상화될 수 있습니다."
    )

with st.container(border=True):
    selected_item = st_searchbox(
        lambda term: search_companies(term, KRX_LISTING),
        default=st.session_state.get("last_selected", None),
        key="stock_searchbox",
        placeholder="종목명 또는 종목코드 입력 (예: 삼성전자, 005930)"
    )

# 유효한 선택이면 저장, 아니면 마지막 저장값 사용
if selected_item and "(" in selected_item:
    st.session_state["last_selected"] = selected_item
    st.session_state["dashboard_ready"] = True
elif st.session_state.get("dashboard_ready"):
    selected_item = st.session_state["last_selected"]
else:
    render_landing()
    st.stop()

selected_company = selected_item.split(" (")[0]
ticker_input = selected_item.split(" (")[1].replace(")", "").strip()

st.success(f"✅ **{selected_company}**({ticker_input}) 대시보드를 안정적으로 로드했습니다.")
st.markdown("---")

df, market_suffix = load_price_data(ticker_input)
fundamentals = get_fundamental_data(ticker_input)
sector = fundamentals["sector"]
is_kosdaq = (market_suffix == ".KQ")

try:
    if df.empty:
        raise ValueError("데이터를 찾을 수 없습니다.")
        
    df = df.reset_index()
    dates_cleaned = df['Date'].squeeze()
    close_cleaned = df['Close'].squeeze()
    dates_korean = pd.to_datetime(dates_cleaned).dt.strftime('%Y.%m.%d')
    
    current_price = int(close_cleaned.iloc[-1])
    prev_price = int(close_cleaned.iloc[-2])
    change_pct = ((current_price - prev_price) / prev_price) * 100
    
    high_cleaned = df['High'].squeeze() if 'High' in df.columns else None
    low_cleaned  = df['Low'].squeeze()  if 'Low'  in df.columns else None    
    volume_series = df['Volume'].squeeze() if 'Volume' in df.columns else pd.Series(dtype=float)

    naver_posts = get_naver_discussion_by_likes(ticker_input)
    community_raw, ai_reason, community_score, volatility_warning = analyze_combined_sentiment(
        naver_posts,
        close_series=close_cleaned,
        high_series=high_cleaned,
        low_series=low_cleaned
    )

    foreign_data = get_foreign_net_buying(ticker_input)
    news_data = get_news_vacuum(ticker_input)
    obj_indicators, objective_score = calculate_objective_indicators(
    close_cleaned, volume_series, foreign_data, news_data, is_kosdaq, high_cleaned, low_cleaned
)
    fomo_data = calculate_fomo_index(ticker_input)
    final_scream_score, scream_tier = calculate_final_score(
        obj_indicators, community_raw, is_kosdaq, fomo_data["score"]
    )
    entry = get_entry_signal(obj_indicators, final_scream_score)
        # 가격 기반 / 수급 기반 그룹 헤더로 구분
    price_keys = [
        ("rsi",      "📈 RSI (14일)"),
        ("bb",       "〰️ 볼린저 밴드"),
        ("w52",      "📉 52주 신저가"),
        ("drawdown", "📉 고점 대비 낙폭"),  # 신규
        ("ichimoku", "☁️ 일목균형표"),
        ]
    supply_keys = [
        ("volume",      "🔊 거래량 폭발"),
        ("pvd",         "💥 공포-거래량 괴리"),
        ("foreign",     "🌍 외국인 동향"),
        ("obv", "📊 OBV 다이버전스")
        ]

    col_main, col_side = st.columns([6, 4])

    with col_main:
        render_company_header(selected_company, ticker_input, sector)
        tab_line, tab_candle = st.tabs(["라인", "캔들"])
        with tab_line:
            with st.container(border=True):
                render_stock_chart(dates_korean, close_cleaned)
        with tab_candle:
            with st.container(border=True):
                render_candle_chart(df, months=2)

        ant_refund_line = calc_vwap_refund_line(df)
        fib = calc_fibonacci_nearest(close_cleaned)
        render_price_info(current_price, change_pct, ant_refund_line, fib, volatility_warning)
        render_fundamental_stats(fundamentals) 

        tab_price, tab_supply = st.tabs(["가격 기반", "수급 기반"])
    with tab_price:
        render_indicator_group(price_keys, obj_indicators)
    with tab_supply:
        render_indicator_group(supply_keys, obj_indicators)

    with col_side:
        render_entry_card(entry)
        render_gauge_and_tier(final_scream_score, scream_tier)
        render_score_metrics(community_raw, objective_score)
        render_signal_summary(obj_indicators)
        render_fomo_panel(fomo_data)
        st.markdown("---")
        render_community_tab(naver_posts)
        
except Exception as e:
    st.error(f"⚠️ 대시보드 로드 중 치명적인 문제가 발생했습니다. (에러: {e})")
    st.exception(e)