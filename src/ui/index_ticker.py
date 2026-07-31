import streamlit as st
from constants import PRICE_COLOR, THEME
from core.market_index import get_market_index_series, get_usdkrw_data
from ui.common import html_block

def _build_sparkline_svg(series, color, width=100, height=32):
    if series is None or len(series) < 2:
        return ""
    values = series.tail(30).tolist()
    vmin, vmax = min(values), max(values)
    vrange = (vmax - vmin) or 1
    step = width / (len(values) - 1)
    points = [
        f"{i*step:.1f},{height - ((v - vmin) / vrange * height):.1f}"
        for i, v in enumerate(values)
    ]
    return f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'


def render_index_ticker(results=None, usdkrw_data=None):
    # 1. 데이터 로드
    kospi_series, _ = get_market_index_series(False)
    kosdaq_series, _ = get_market_index_series(True)
    
    # 2. 원/달러 환율 데이터 로드 (내부에서 직접 호출)
    usdkrw_data = get_usdkrw_data()

    # 2. 종합 공포지수 로직
    fear_score = 50.0
    if results:
        all_scores = [
            r["score"] for r in results.get("kospi", []) + results.get("kosdaq", [])
        ]
        if all_scores:
            fear_score = sum(all_scores) / len(all_scores)

    if fear_score >= 65:
        fear_label = "극심한 공포 (매수)"
        fear_color = "#DC2626"
        fear_bg = "rgba(220, 38, 38, 0.12)"
    elif fear_score >= 45:
        fear_label = "중립 / 경계"
        fear_color = "#D97706"
        fear_bg = "rgba(217, 119, 6, 0.12)"
    else:
        fear_label = "탐욕 / 안정"
        fear_color = "#2563EB"
        fear_bg = "rgba(37, 99, 235, 0.12)"

    # 반응형 그리드 CSS
    css = f"""
    <style>
    /* 기본 데스크톱: 무조건 4열(1x4) 유지 */
    .ticker-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 20px;
        width: 100%;
    }}

    /* 태블릿 / 중형 화면 (900px 이하): 2열(2x2)로 깔끔하게 배치 */
    @media (max-width: 900px) {{
        .ticker-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}

    /* 모바일 화면 (550px 이하): 1열로 나열 */
    @media (max-width: 550px) {{
        .ticker-grid {{
            grid-template-columns: 1fr;
        }}
    }}

    .ticker-card {{
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.015) 100%);
        border: 1px solid {THEME['border']};
        border-top: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        padding: 12px 14px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        box-sizing: border-box;
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease, border-color 0.25s ease;
    }}

    .ticker-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border-color: rgba(200, 200, 200, 0.4);
    }}

    .ticker-info {{
        display: flex;
        flex-direction: column;
        gap: 2px;
        min-width: 0;
    }}

    .ticker-title {{
        font-size: 11.5px;
        font-weight: 700;
        color: {THEME['text_sub']};
        white-space: nowrap;
    }}

    .ticker-value {{
        font-size: 16px;
        font-weight: 800;
        color: {THEME['text_main']};
        line-height: 1.2;
        white-space: nowrap;
    }}

    .ticker-sub {{
        font-size: 11px;
        font-weight: 700;
        white-space: nowrap;
    }}

    .fear-badge {{
        font-size: 10px;
        font-weight: 800;
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
        margin-top: 2px;
        white-space: nowrap;
    }}

    .ticker-svg-box {{
        flex-shrink: 0;
    }}
    </style>
    """

    def _make_index_card_html(label, series):
        if series is None or len(series) < 2:
            return f"""
            <div class="ticker-card">
                <div class="ticker-info">
                    <span class="ticker-title">{label}</span>
                    <span style="font-size:11px; color:{THEME['text_sub']};">수집 실패</span>
                </div>
            </div>
            """
        current = float(series.iloc[-1])
        prev = float(series.iloc[-2])
        change_pct = (current - prev) / prev * 100
        p_color = PRICE_COLOR["up"] if change_pct >= 0 else PRICE_COLOR["down"]
        arrow = "▲" if change_pct >= 0 else "▼"
        spark = _build_sparkline_svg(series, p_color)

        return f"""
        <div class="ticker-card">
            <div class="ticker-info">
                <span class="ticker-title">{label}</span>
                <span class="ticker-value">{current:,.2f}</span>
                <span class="ticker-sub" style="color:{p_color};">{arrow} {change_pct:+.2f}%</span>
            </div>
            <div class="ticker-svg-box">
                <svg width="76" height="30" viewBox="0 0 100 32">{spark}</svg>
            </div>
        </div>
        """

    kospi_html = _make_index_card_html("코스피", kospi_series)
    kosdaq_html = _make_index_card_html("코스닥", kosdaq_series)

    fear_html = f"""
    <div class="ticker-card">
        <div class="ticker-info">
            <span class="ticker-title">시장 종합 공포지수</span>
            <span class="ticker-value" style="color:{fear_color};">{fear_score:.1f} <span style="font-size:11px;">점</span></span>
            <div><span class="fear-badge" style="color:{fear_color}; background:{fear_bg};">{fear_label}</span></div>
        </div>
    </div>
    """

# 4) 원/달러 환율 HTML (차트 및 데이터 연동 강화)
    if usdkrw_data and usdkrw_data.get("series") is not None:
        rate = usdkrw_data.get("current", 0.0)
        chg = usdkrw_data.get("change_pct", 0.0)
        r_color = PRICE_COLOR["up"] if chg >= 0 else PRICE_COLOR["down"]
        r_arrow = "▲" if chg >= 0 else "▼"
        
        # 코스피/코스닥과 동일하게 Sparkline SVG 차트 생성
        r_spark = _build_sparkline_svg(usdkrw_data.get("series"), r_color)
        
        fx_html = f"""
        <div class="ticker-card">
            <div class="ticker-info">
                <span class="ticker-title">원/달러 환율</span>
                <span class="ticker-value">{rate:,.1f}원</span>
                <span class="ticker-sub" style="color:{r_color};">{r_arrow} {chg:+.2f}%</span>
            </div>
            <div class="ticker-svg-box">
                <svg width="76" height="30" viewBox="0 0 100 32">{r_spark}</svg>
            </div>
        </div>
        """
    else:
        # 환율 데이터가 없을 때의 기본/실패 처리
        fx_html = f"""
        <div class="ticker-card">
            <div class="ticker-info">
                <span class="ticker-title">원/달러 환율</span>
                <span class="ticker-value" style="font-size:13px; color:{THEME['text_sub']};">데이터 불러오기 실패</span>
            </div>
        </div>
        """

    full_html = f"""
    {css}
    <div class="ticker-grid">
        {kospi_html}
        {kosdaq_html}
        {fear_html}
        {fx_html}
    </div>
    """

    html_block(full_html)