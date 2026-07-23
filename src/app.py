import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from ui.common import render_tab_group

from core.krx_listing import load_krx_listing, search_companies
from core.price_data import load_price_data
from core.naver_scraper import get_naver_discussion_by_likes, get_foreign_net_buying, get_news_vacuum
from core.sentiment import analyze_combined_sentiment
from core.indicators import calculate_objective_indicators
from core.scoring import calculate_fomo_index, calculate_final_score, get_entry_signal
from core.price_levels import calc_vwap_refund_line, calc_fibonacci_nearest
from core.fundamentals import get_fundamental_data
from core.market_index import get_market_index_series, calculate_rs_indicator
from core.risk_levels import calculate_risk_levels
from core.scanner import run_fear_scanner
from core.score_tracker import record_and_get_delta

from ui.scanner_panel import render_fear_scanner
from ui.landing import render_landing
from ui.chart import render_stock_chart, render_candle_chart 
from ui.main_panel import render_price_info, render_community_tab, render_fundamental_stats
from ui.sidebar_cards import (
    render_entry_card, render_gauge_and_tier, render_score_metrics,
    render_signal_summary, render_fomo_panel, render_indicator_group, 
    render_risk_card
)
from ui.ticker_badge import render_company_header
from ui.index_ticker import render_index_ticker

from constants import THEME, ACCENT
from streamlit_searchbox import st_searchbox

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="개미반대로 (Ant-Contra)")

if "home" in st.query_params:
    st.session_state.pop("last_selected", None)
    st.session_state.pop("dashboard_ready", None)
    st.query_params.clear()
    st.rerun()
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
    border-radius:9px; padding:6px 14px; color:{THEME['text_sub']};
    font-weight:600; font-size:13.5px; transition:0.15s;
}}
div[data-baseweb="tab-panel"] {{ padding-top: 2px !important; }}
button[data-baseweb="tab"][aria-selected="true"] {{
    background:{THEME['surface']}; color:{ACCENT};
    box-shadow:0 1px 3px rgba(0,0,0,0.12);
}}
div[data-baseweb="tab-highlight"] {{ display:none; }}
div[data-baseweb="tab-border"] {{ display:none; }}
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
div[data-testid="stWidgetLabel"] {{
    display: none !important;
}}
div[data-testid="stRadio"] {{
    margin: 2px 0 2px 0 !important;
    padding: 0 !important;
}}
div[data-testid="stRadio"] > div[role="radiogroup"] {{
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 8px !important;
    margin: 0 !important; padding: 0 !important;
}}
div[data-testid="stRadio"] label[data-baseweb="radio"] {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: relative !important;
    margin: 0 !important;
    border: 1px solid #2b2b2b !important;
    border-radius: 999px !important;
    padding: 7px 18px !important;
    min-height: 0 !important;
    background: #2b2b2b !important;
    cursor: pointer;
    transition: transform 0.3s cubic-bezier(0.19, 1, 0.22, 1),
                background-color 0.25s ease,
                border-color 0.25s ease;
}}
/* label 바로 아래 모든 div 껍데기를 렌더링 트리에서 제거 → p가 label의 직계 flex 자식이 됨 */
div[data-testid="stRadio"] label[data-baseweb="radio"] > div {{
    display: contents !important;
}}
div[data-testid="stRadio"] label[data-baseweb="radio"] > div:not(:has(p)) {{
    display: none !important;
}}
/* 네이티브 radio input은 완전히 숨김 (레이아웃에서 제외) */
div[data-testid="stRadio"] label[data-baseweb="radio"] input[type="radio"] {{
    position: absolute !important;
    opacity: 0 !important;
    width: 0 !important; height: 0 !important;
    margin: 0 !important; padding: 0 !important;
    pointer-events: none !important;
}}
div[data-testid="stRadio"] label[data-baseweb="radio"] p {{
    margin: 0 !important;
    padding: 0 !important;
    font-size: 12.5px !important;
    line-height: 1 !important;
    font-weight: 700 !important;
    color: #9ca3af !important;
    white-space: nowrap;
    transition: color 0.25s ease;
}}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {{
    background: {ACCENT} !important;
    border-color: {ACCENT} !important;
    transform: scale(1.06);
}}
div[data-testid="stRadio"] label[data-baseweb="radio"]:not(:has(input:checked)) {{
    border-color: {ACCENT}55 !important;
}}
div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p {{
    color: #1a1a1a !important;
}}
</style>
""", unsafe_allow_html=True)

is_detail_view = bool(st.session_state.get("dashboard_ready")) or ("stock" in st.query_params)

with st.container(key="app_header_top"):
    st.markdown(
        "<style>div.st-key-app_header_top [data-testid='stElementContainer']{margin-bottom:0 !important;}</style>",
        unsafe_allow_html=True
    )
    st.markdown(f"""
<a href="?home=1" target="_self" style="text-decoration:none;">
<div style="font-size:20px; font-weight:800; color:{THEME['text_main']}; margin-bottom:6px; width:fit-content; cursor:pointer;">개미반대로</div>
</a>
""", unsafe_allow_html=True)

    if not is_detail_view:
        st.markdown(f"""
<div style="margin-bottom:2px;">
<div style="background:{ACCENT}14; border-radius:999px; padding:7px 16px; margin-bottom:4px;
     display:inline-flex; align-items:center; gap:6px; width:fit-content;">
<span style="font-size:11.5px; color:{THEME['text_main']}; font-weight:600; white-space:nowrap;">
⚡ 실시간 여론 × 기술적 지표로 군중의 공포를 찾는 역발상 스캐너
</span>
</div>
<div style="font-size:10.5px; color:{THEME['text_sub']}; padding-left:2px;">
😱 통합 공포지수 &nbsp;·&nbsp; 📊 RSI·볼린저·수급 분석 &nbsp;·&nbsp; 🔥 개미 FOMO 탐지 &nbsp;·&nbsp; 💬 네이버 실시간 여론
</div>
</div>
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

if not is_detail_view:
    render_index_ticker()

# 유효한 선택이면 저장, 아니면 마지막 저장값 사용
if selected_item and "(" in selected_item:
    st.session_state["last_selected"] = selected_item
    st.session_state["dashboard_ready"] = True
elif st.session_state.get("dashboard_ready"):
    selected_item = st.session_state["last_selected"]
elif "stock" in st.query_params:
    selected_item = st.query_params["stock"]
    st.session_state["last_selected"] = selected_item
    st.session_state["dashboard_ready"] = True
else:
    render_landing()
    with st.spinner("공포 스캐너 실행 중..."):
        scan_results = run_fear_scanner(top_n=10)
    render_fear_scanner(scan_results, KRX_LISTING)
    st.stop()

st.query_params["stock"] = selected_item

selected_company = selected_item.split(" (")[0]
ticker_input = selected_item.split(" (")[1].replace(")", "").strip()

st.success(f"✅ **{selected_company}**({ticker_input}) 대시보드를 안정적으로 로드했습니다.")
st.markdown("<hr style='margin-top:4px; margin-bottom:14px;'>", unsafe_allow_html=True)

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
    index_series = get_market_index_series(is_kosdaq)
    rs_data = calculate_rs_indicator(close_cleaned, index_series)
    obj_indicators, objective_score = calculate_objective_indicators(
        close_cleaned, volume_series, foreign_data, news_data, is_kosdaq, high_cleaned, low_cleaned, rs_data
    )
    fomo_data = calculate_fomo_index(ticker_input)
    final_scream_score, scream_tier = calculate_final_score(
        obj_indicators, community_raw, is_kosdaq, fomo_data["score"]
    )
    score_delta = record_and_get_delta(ticker_input, final_scream_score)
    risk_levels = calculate_risk_levels(close_cleaned, high_cleaned, low_cleaned, current_price)
    entry = get_entry_signal(obj_indicators, final_scream_score, risk_levels)
        # 가격 기반 / 수급 기반 그룹 헤더로 구분
    price_keys = [
        ("rsi",      "📈 RSI (14일)"),
        ("bb",       "〰️ 볼린저 밴드"),
        ("w52",      "📉 52주 신저가"),
        ("drawdown", "📉 고점 대비 낙폭"),  # 신규
        ("ichimoku", "☁️ 일목균형표"),
        ("rs",       "🏁 시장대비 상대강도"),
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
        chart_mode = render_tab_group(["라인", "캔들"], key="chart_mode_toggle", margin_bottom="-10px")


        if chart_mode == "라인":
            with st.container(border=True, key="line_chart_box"):
                render_stock_chart(dates_korean, close_cleaned, volume_series)
        else:
            render_candle_chart(df)

        ant_refund_line = calc_vwap_refund_line(df)
        fib = calc_fibonacci_nearest(close_cleaned)
        render_price_info(current_price, change_pct, ant_refund_line, fib, volatility_warning)
        render_fundamental_stats(fundamentals)
        st.markdown(f"<hr style='border:none; border-top:1px solid {THEME['border']}; margin:14px 0 12px 0;'>", unsafe_allow_html=True)

        indicator_mode = render_tab_group(["가격 기반", "수급 기반"], key="indicator_mode_toggle")

        if indicator_mode == "가격 기반":
            render_indicator_group(price_keys, obj_indicators)
        else:
            render_indicator_group(supply_keys, obj_indicators)

    with col_side:
        render_entry_card(entry)
        render_risk_card(risk_levels)
        render_gauge_and_tier(final_scream_score, scream_tier, score_delta)
        render_score_metrics(community_raw, objective_score)
        render_signal_summary(obj_indicators)
        render_fomo_panel(fomo_data)
        st.markdown("---")
        render_community_tab(naver_posts)
        
except Exception as e:
    st.error(f"⚠️ 대시보드 로드 중 치명적인 문제가 발생했습니다. (에러: {e})")
    st.exception(e)