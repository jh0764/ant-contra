from urllib.parse import quote
import streamlit as st
from constants import PRICE_COLOR, THEME
from ui.common import html_block


def _render_row(r, name, rank, is_last):
    p_color = PRICE_COLOR["up"] if r["change_pct"] >= 0 else PRICE_COLOR["down"]
    arrow = "▲" if r["change_pct"] >= 0 else "▼"

    if r["score"] >= 65:
        score_color = "#DC2626"
        score_bg = "rgba(220, 38, 38, 0.08)"
    elif r["score"] >= 45:
        score_color = "#D97706"
        score_bg = "rgba(217, 119, 6, 0.08)"
    else:
        score_color = THEME["text_sub"]
        score_bg = "rgba(156, 163, 175, 0.08)"

    if rank == 1:
        rank_badge = '<span class="rank-tag rank-1">1</span>'
    elif rank == 2:
        rank_badge = '<span class="rank-tag rank-2">2</span>'
    elif rank == 3:
        rank_badge = '<span class="rank-tag rank-3">3</span>'
    else:
        rank_badge = f'<span class="rank-tag rank-default">{rank}</span>'

    stock_qp = quote(f"{name} ({r['code']})", safe="")
    border_style = "" if is_last else f"border-bottom: 1px solid {THEME['border']};"

    return f"""
    <a href="?stock={stock_qp}" target="_self" class="scanner-row-link">
        <div class="scanner-row" style="{border_style}">
            <div class="scanner-row-left">
                {rank_badge}
                <div class="scanner-row-info">
                    <span class="scanner-row-name">{name}</span>
                    <span class="scanner-row-code">{r['code']}</span>
                </div>
            </div>
            <div class="scanner-row-right">
                <span class="scanner-price" style="color:{p_color};">{arrow} {r['change_pct']:+.2f}%</span>
                <span class="scanner-score-badge" style="color:{score_color}; background:{score_bg};">{r['score']}점</span>
            </div>
        </div>
    </a>
    """


def _render_column(badge_html, results, name_map):
    if not results:
        return f"""
        <div class="scanner-panel">
            <div class="scanner-panel-header">{badge_html}</div>
            <div class="scanner-empty-box">스캔 결과 없음</div>
        </div>
        """

    total_count = len(results)
    rows = "".join(
        _render_row(r, name_map.get(r["code"], r["code"]), idx + 1, idx == total_count - 1)
        for idx, r in enumerate(results)
    )
    return f"""
    <div class="scanner-panel">
        <div class="scanner-panel-header">{badge_html}</div>
        <div class="scanner-list-container">{rows}</div>
    </div>
    """


def render_fear_scanner(results, krx_listing):
    name_map = dict(zip(krx_listing["Code"], krx_listing["Name"]))

    css = f"""
    <style>
    /* 헤더 컨테이너 레이아웃 정렬 */
    .scanner-header-top {{
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        width: 100% !important;
        margin-bottom: 6px !important;
    }}

    .scanner-header-title {{
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #0F172A !important;
        letter-spacing: -0.4px !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }}
    
    .scanner-live-dot {{
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }}

    /* ──────────────────────────────────────────────────────────
       Uiverse 기반 CTA (Call-To-Action) 미니멀 인터랙션 스타일
       ────────────────────────────────────────────────────────── */
.cta-backtest {{
        margin-left: auto !important;
        border: none !important;
        background: none !important;
        cursor: pointer !important;
        display: inline-flex !important;
        align-items: center !important;
        text-decoration: none !important;
        padding: 4px 0 !important;
    }}

    .cta-backtest .hover-underline-animation {{
        position: relative !important;
        color: #334155 !important;
        font-size: 12.5px !important;
        font-weight: 600 !important;
        letter-spacing: -0.2px !important;
        padding-bottom: 2px !important;
        padding-right: 8px !important;
    }}

    /* 밑줄 드로잉 애니메이션 */
    .cta-backtest .hover-underline-animation:after {{
        content: "" !important;
        position: absolute !important;
        width: 100% !important;
        transform: scaleX(0) !important;
        height: 1.5px !important;
        bottom: 0 !important;
        left: 0 !important;
        background-color: #334155 !important;
        transform-origin: bottom right !important;
        transition: transform 0.25s ease-out !important;
    }}

    /* 호버 시 글자색 고정 */
    .cta-backtest:hover .hover-underline-animation {{
        color: #334155 !important;
    }}

    .cta-backtest:hover .hover-underline-animation:after {{
        transform: scaleX(1) !important;
        transform-origin: bottom left !important;
    }}

    /* SVG 화살표 슬라이드 애니메이션 */
    .cta-backtest svg {{
        width: 14px;
        height: 14px;
        stroke: #475569;
        stroke-width: 2;
        fill: none;
        transform: translateX(0);
        transition: all 0.3s ease !important;
    }}

    .cta-backtest:hover svg {{
        stroke: #0F172A !important;
        transform: translateX(5px) !important;
    }}

    .cta-backtest:active svg {{
        transform: scale(0.9) translateX(5px) !important;
    }}

    .scanner-header-desc {{
        font-size: 12px !important;
        color: #64748B !important;
        margin-bottom: 14px !important;
        line-height: 1.4 !important;
        letter-spacing: -0.2px !important;
    }}

    .scanner-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
        gap: 18px;
    }}

    /* 이하 기존 리스트 스캐너 카드 CSS 유지 */
    .scanner-panel {{
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.015) 100%);
        border: 1px solid {THEME['border']};
        border-top: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        overflow: hidden;
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease;
    }}

    .scanner-panel:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        border-color: rgba(200, 200, 200, 0.4);
    }}

    .scanner-panel-header {{
        padding: 10px 14px;
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid {THEME['border']};
        display: flex;
        align-items: center;
    }}

    .market-badge {{
        font-size: 11px;
        font-weight: 800;
        padding: 3px 8px;
        border-radius: 5px;
        letter-spacing: 0.4px;
        line-height: 1;
    }}

    .market-badge.kospi {{ background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }}
    .market-badge.kosdaq {{ background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }}
    .scanner-list-container {{ background: transparent; }}
    .scanner-row-link {{ text-decoration: none !important; display: block; }}
    .scanner-row {{ padding: 9.5px 14px; display: flex; justify-content: space-between; align-items: center; transition: background-color 0.18s ease, transform 0.18s cubic-bezier(0.16, 1, 0.3, 1); }}
    .scanner-row-link:hover .scanner-row {{ background-color: rgba(255, 255, 255, 0.08); transform: translateX(3px); }}
    .scanner-row-left {{ display: flex; align-items: center; gap: 10px; min-width: 0; }}
    .rank-tag {{ width: 18px; height: 18px; border-radius: 4px; font-size: 11px; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: transform 0.18s ease; }}
    .scanner-row-link:hover .rank-tag {{ transform: scale(1.1); }}
    .rank-1 {{ background: #FEF3C7; color: #D97706; }}
    .rank-2 {{ background: #F1F5F9; color: #475569; }}
    .rank-3 {{ background: #FFEDD5; color: #C2410C; }}
    .rank-default {{ background: transparent; color: {THEME['text_sub']}; opacity: 0.5; }}
    .scanner-row-info {{ display: flex; flex-direction: column; gap: 1px; min-width: 0; }}
    .scanner-row-name {{ font-size: 13px; font-weight: 700; color: {THEME['text_main']}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.2; }}
    .scanner-row-code {{ font-size: 10px; font-weight: 500; color: {THEME['text_sub']}; opacity: 0.6; }}
    .scanner-row-right {{ display: flex; align-items: center; gap: 10px; flex-shrink: 0; }}
    .scanner-price {{ font-size: 12px; font-weight: 700; letter-spacing: -0.2px; }}
    .scanner-score-badge {{ font-size: 11px; font-weight: 800; padding: 2px 7px; border-radius: 5px; min-width: 36px; text-align: center; }}
    .scanner-empty-box {{ padding: 24px 0; text-align: center; font-size: 11.5px; color: {THEME['text_sub']}; }}
    </style>
    """

    kospi_badge = '<span class="market-badge kospi">KOSPI</span>'
    kosdaq_badge = '<span class="market-badge kosdaq">KOSDAQ</span>'

    kospi_html = _render_column(kospi_badge, results.get("kospi", []), name_map)
    kosdaq_html = _render_column(kosdaq_badge, results.get("kosdaq", []), name_map)

    # HTML Structure (Uiverse CTA 인터랙션 적용)
    header_html = f"""
    {css}
    <div class="scanner-header-top">
        <div class="scanner-header-title">
            <span class="scanner-live-dot"></span>
            실시간 과매도 / 공포 지수 모니터
        </div>
        <a href="?view=backtest" target="_self" class="cta-backtest">
            <span class="hover-underline-animation">백테스트 성과 분석</span>
            <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
        </a>
    </div>
    <div class="scanner-header-desc">주요 대형주 유니버스 대상 시장별 과매도 강도 상위 10개 종목 스캔 결과입니다.</div>
    <div class="scanner-grid">{kospi_html}{kosdaq_html}</div>
    """

    html_block(header_html)