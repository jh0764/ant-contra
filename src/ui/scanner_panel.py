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
    /* 헤더 영역 */
    .scanner-header-title {{
        font-size: 18px;
        font-weight: 800;
        color: {THEME['text_main']};
        margin-bottom: 4px;
        letter-spacing: -0.3px;
    }}
    .scanner-header-desc {{
        font-size: 11.5px;
        color: {THEME['text_sub']};
        margin-bottom: 16px;
        opacity: 0.85;
    }}

    .scanner-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
        gap: 18px;
    }}

    /* 통합 카드 패널 (투명 배경 + 부드러운 패널 호버 애니메이션) */
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

    /* 카드 패널 호버 효과 */
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

    .market-badge.kospi {{
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
    }}

    .market-badge.kosdaq {{
        background: #ECFDF5;
        color: #047857;
        border: 1px solid #A7F3D0;
    }}

    /* 리스트 및 행(Row) 애니메이션 */
    .scanner-list-container {{
        background: transparent;
    }}

    .scanner-row-link {{
        text-decoration: none !important;
        display: block;
    }}

    .scanner-row {{
        padding: 9.5px 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background-color 0.18s ease, transform 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    /* 리스트 행 마우스 호버 효과: 배경 하이라이트 + 3px 우측 이동 */
    .scanner-row-link:hover .scanner-row {{
        background-color: rgba(255, 255, 255, 0.08);
        transform: translateX(3px);
    }}

    .scanner-row-left {{
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 0;
    }}

    .rank-tag {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 800;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        transition: transform 0.18s ease;
    }}

    /* 호버 시 1~3위 순위 배지 살짝 확대 */
    .scanner-row-link:hover .rank-tag {{
        transform: scale(1.1);
    }}

    .rank-1 {{ background: #FEF3C7; color: #D97706; }}
    .rank-2 {{ background: #F1F5F9; color: #475569; }}
    .rank-3 {{ background: #FFEDD5; color: #C2410C; }}
    .rank-default {{ background: transparent; color: {THEME['text_sub']}; opacity: 0.5; }}

    .scanner-row-info {{
        display: flex;
        flex-direction: column;
        gap: 1px;
        min-width: 0;
    }}

    .scanner-row-name {{
        font-size: 13px;
        font-weight: 700;
        color: {THEME['text_main']};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.2;
    }}

    .scanner-row-code {{
        font-size: 10px;
        font-weight: 500;
        color: {THEME['text_sub']};
        opacity: 0.6;
    }}

    .scanner-row-right {{
        display: flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
    }}

    .scanner-price {{
        font-size: 12px;
        font-weight: 700;
        letter-spacing: -0.2px;
    }}

    .scanner-score-badge {{
        font-size: 11px;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 5px;
        min-width: 36px;
        text-align: center;
    }}

    .scanner-empty-box {{
        padding: 24px 0;
        text-align: center;
        font-size: 11.5px;
        color: {THEME['text_sub']};
    }}
    </style>
    """

    kospi_badge = '<span class="market-badge kospi">KOSPI</span>'
    kosdaq_badge = '<span class="market-badge kosdaq">KOSDAQ</span>'

    kospi_html = _render_column(kospi_badge, results.get("kospi", []), name_map)
    kosdaq_html = _render_column(kosdaq_badge, results.get("kosdaq", []), name_map)

    header_html = f"""
    {css}
    <div class="scanner-header-title">실시간 과매도 / 공포 지수 모니터</div>
    <div class="scanner-header-desc">주요 대형주 유니버스 대상 시장별 과매도 강도 상위 10개 종목 스캔 결과입니다.</div>
    <div class="scanner-grid">{kospi_html}{kosdaq_html}</div>
    """

    html_block(header_html)