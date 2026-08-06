from urllib.parse import quote
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
        _render_row(
            r, name_map.get(r["code"], r["code"]), idx + 1, idx == total_count - 1
        )
        for idx, r in enumerate(results)
    )
    return f"""
    <div class="scanner-panel">
        <div class="scanner-panel-header">{badge_html}</div>
        <div class="scanner-list-container">{rows}</div>
    </div>
    """


def _build_sector_grid_html(results, name_map):
    sector_buckets = {
        "반도체": [],
        "2차전지": [],
        "자동차/부품": [],
        "제약/바이오": [],
        "금융/지주": [],
        "IT/플랫폼": [],
        "조선/해운": [],
        "방산/우주": [],
        "철강/소재": [],
        "화학/에너지": [],
    }

    all_items = results.get("kospi", []) + results.get("kosdaq", [])
    for item in all_items:
        code = item.get("code", "")
        name = name_map.get(code, item.get("name", ""))
        score = item.get("score", 50)
        sec = item.get("sector", "")

        if "반도체" in sec or "하이닉스" in name or "전자" in name:
            sector_buckets["반도체"].append(score)
        elif "전지" in sec or "에너지" in name:
            sector_buckets["2차전지"].append(score)
        elif "운수" in sec or "자동차" in sec or "모빌리티" in name:
            sector_buckets["자동차/부품"].append(score)
        elif "바이오" in sec or "제약" in sec or "케어" in name:
            sector_buckets["제약/바이오"].append(score)
        elif "금융" in sec or "지주" in sec or "은행" in name or "화재" in name:
            sector_buckets["금융/지주"].append(score)
        elif "조선" in sec or "해운" in sec or "중공업" in name:
            sector_buckets["조선/해운"].append(score)
        elif "방산" in sec or "항공" in sec or "우주" in name:
            sector_buckets["방산/우주"].append(score)
        elif "철강" in sec or "금속" in sec or "제강" in name:
            sector_buckets["철강/소재"].append(score)
        elif "화학" in sec or "정유" in sec:
            sector_buckets["화학/에너지"].append(score)
        else:
            sector_buckets["IT/플랫폼"].append(score)

    defaults = {
        "반도체": 38.0,
        "2차전지": 62.5,
        "자동차/부품": 42.0,
        "제약/바이오": 41.5,
        "금융/지주": 48.0,
        "IT/플랫폼": 40.8,
        "조선/해운": 52.4,
        "방산/우주": 35.1,
        "철강/소재": 49.3,
        "화학/에너지": 57.8,
    }

    cards_html = ""
    for name, def_val in defaults.items():
        scores = sector_buckets.get(name, [])
        avg_score = sum(scores) / len(scores) if scores else def_val

        if avg_score >= 65:
            badge_color = "#DC2626"
            badge_bg = "rgba(220, 38, 38, 0.08)"
            status_text = "공포 집중"
        elif avg_score >= 45:
            badge_color = "#D97706"
            badge_bg = "rgba(217, 119, 6, 0.08)"
            status_text = "중립"
        else:
            badge_color = THEME["text_sub"]
            badge_bg = "rgba(156, 163, 175, 0.08)"
            status_text = "안정"

        cards_html += f"""
        <div class="sector-card">
            <div class="sector-card-top">
                <span class="sector-card-name">{name}</span>
                <span class="sector-badge" style="color:{badge_color}; background:{badge_bg};">{status_text}</span>
            </div>
            <div class="sector-card-body">
                <span class="sector-card-score">{avg_score:.1f}<span class="sector-unit">점</span></span>
            </div>
            <div class="sector-bar-bg">
                <div class="sector-bar-fill" style="width:{min(max(avg_score, 0), 100)}%; background:{badge_color};"></div>
            </div>
        </div>
        """

    return f"""
    <div class="sector-container">
        <div class="sector-header-title">업종 / 섹터별 공포 지수</div>
        <div class="sector-header-desc">주요 산업 섹터별 평균 비명지수 및 공포 집중도 분포</div>
        <div class="sector-grid">{cards_html}</div>
    </div>
    """


def _eval_supply_status(mkt, foreign_val, inst_val):
    if mkt == "kospi":
        strong_th, meaningful_th = 5000, 2000
        ssang_f, ssang_i = 1500, 1000
    else:  # kosdaq
        strong_th, meaningful_th = 1500, 600
        ssang_f, ssang_i = 500, 400

    def _get_badge(val):
        if val >= strong_th:
            return "강력 매수", "#DC2626", "rgba(220, 38, 38, 0.1)"
        elif val >= meaningful_th:
            return "유의미 매수", "#EA580C", "rgba(234, 88, 12, 0.1)"
        elif val > 0:
            return "소폭 매수", "#64748B", "rgba(100, 116, 139, 0.1)"
        elif val <= -strong_th:
            return "강력 매도", "#2563EB", "rgba(37, 99, 235, 0.1)"
        elif val <= -meaningful_th:
            return "유의미 매도", "#2563EB", "rgba(37, 99, 235, 0.1)"
        else:
            return "소폭 매도", "#64748B", "rgba(100, 116, 139, 0.1)"

    f_txt, f_col, f_bg = _get_badge(foreign_val)
    i_txt, i_col, i_bg = _get_badge(inst_val)

    is_ssang = (foreign_val >= ssang_f) and (inst_val >= ssang_i)

    return {
        "f_txt": f_txt,
        "f_col": f_col,
        "f_bg": f_bg,
        "i_txt": i_txt,
        "i_col": i_col,
        "i_bg": i_bg,
        "is_ssang": is_ssang,
    }


def render_fear_scanner(results, krx_listing, supply_data=None):
    if supply_data is None:
        supply_data = {
            "kospi": {"foreign": 1850, "institution": 1200},
            "kosdaq": {"foreign": -420, "institution": 310},
        }

    name_map = dict(zip(krx_listing["Code"], krx_listing["Name"]))

    kp_eval = _eval_supply_status(
        "kospi", supply_data["kospi"]["foreign"], supply_data["kospi"]["institution"]
    )
    kd_eval = _eval_supply_status(
        "kosdaq", supply_data["kosdaq"]["foreign"], supply_data["kosdaq"]["institution"]
    )

    kp_ssang_html = (
        '<span class="ssang-badge">쌍끌이</span>' if kp_eval["is_ssang"] else ""
    )
    kd_ssang_html = (
        '<span class="ssang-badge">쌍끌이</span>' if kd_eval["is_ssang"] else ""
    )

    def _get_val_class(val):
        return "supply-val-up" if val > 0 else "supply-val-down"

    def _fmt_num(val):
        sign = "+" if val > 0 else ""
        return f"{sign}{val:,}억"

    kp_f_val = supply_data["kospi"]["foreign"]
    kp_i_val = supply_data["kospi"]["institution"]
    kd_f_val = supply_data["kosdaq"]["foreign"]
    kd_i_val = supply_data["kosdaq"]["institution"]

    css = f"""
    <style>
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

    /* 수급 요약 바 전체 메인 컨테이너 */
    .supply-summary-bar {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        align-items: center !important;
        gap: 8px 12px !important;
        background: rgba(255, 255, 255, 0.4) !important;
        border: 1px solid {THEME['border']} !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin-bottom: 14px !important;
        box-sizing: border-box !important;
        width: 100% !important;
        max-width: 100% !important;
        overflow: hidden !important;
    }}

    .supply-title {{
        font-size: 12px !important;
        font-weight: 700 !important;
        color: #334155 !important;
        white-space: nowrap !important;
        flex-shrink: 0 !important;
    }}

    /* KOSPI + KOSDAQ 박스 통합 그룹 래퍼 */
    .supply-content-wrapper {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        align-items: center !important;
        gap: 8px !important;
        flex: 1 1 auto !important;
    }}

    .supply-group {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        align-items: center !important;
        gap: 4px 6px !important;
        font-size: 11px !important;
        color: #64748B !important;
        background: rgba(255, 255, 255, 0.85) !important;
        padding: 4px 8px !important;
        min-height: 26px !important;
        border-radius: 6px !important;
        border: 1px solid rgba(203, 213, 225, 0.8) !important;
        box-sizing: border-box !important;
        max-width: 100% !important;
    }}

    .supply-sub-group {{
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
        white-space: nowrap !important;
    }}

    .supply-market-tag {{
        font-weight: 800 !important;
        font-size: 10.5px !important;
        color: #1E293B !important;
        line-height: 1 !important;
        white-space: nowrap !important;
    }}

    .supply-item-text {{
        font-size: 11px !important;
        color: #475569 !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        gap: 2px !important;
        white-space: nowrap !important;
    }}

    .supply-val-up {{
        color: {PRICE_COLOR['up']} !important;
        font-weight: 700 !important;
    }}

    .supply-val-down {{
        color: {PRICE_COLOR['down']} !important;
        font-weight: 700 !important;
    }}

    .supply-status-badge {{
        font-size: 9.5px !important;
        font-weight: 700 !important;
        padding: 2px 4px !important;
        border-radius: 3px !important;
        line-height: 1 !important;
        display: inline-block !important;
        white-space: nowrap !important;
    }}

    .supply-divider {{
        opacity: 0.3 !important;
        font-size: 9px !important;
        margin: 0 1px !important;
        line-height: 1 !important;
    }}

    .ssang-badge {{
        font-size: 9.5px !important;
        font-weight: 800 !important;
        color: #9333EA !important;
        background: rgba(147, 51, 234, 0.08) !important;
        border: 1px solid rgba(147, 51, 234, 0.25) !important;
        padding: 2px 5px !important;
        border-radius: 4px !important;
        line-height: 1 !important;
        white-space: nowrap !important;
    }}

    /* 반응형 레이아웃 분기 (단계별 정렬) */
    @media (max-width: 820px) {{
        .supply-title {{
            width: 100% !important;
            margin-bottom: 2px !important;
        }}
        .supply-content-wrapper {{
            width: 100% !important;
        }}
    }}

    @media (max-width: 580px) {{
        .supply-content-wrapper {{
            flex-direction: column !important;
            align-items: stretch !important;
        }}
        .supply-group {{
            width: 100% !important;
        }}
    }}

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

    .cta-backtest:hover .hover-underline-animation {{ color: #334155 !important; }}
    .cta-backtest:hover .hover-underline-animation:after {{ transform: scaleX(1) !important; transform-origin: bottom left !important; }}
    .cta-backtest svg {{ width: 14px; height: 14px; stroke: #475569; stroke-width: 2; fill: none; transform: translateX(0); transition: all 0.3s ease !important; }}
    .cta-backtest:hover svg {{ stroke: #0F172A !important; transform: translateX(5px) !important; }}
    .cta-backtest:active svg {{ transform: scale(0.9) translateX(5px) !important; }}

    .scanner-header-desc {{
        font-size: 12px !important;
        color: #64748B !important;
        margin-bottom: 10px !important;
        line-height: 1.4 !important;
        letter-spacing: -0.2px !important;
    }}

    .guide-accordion {{
        background: rgba(255, 255, 255, 0.25);
        border: 1px solid {THEME['border']};
        border-radius: 10px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        overflow: hidden;
    }}

    .guide-summary {{ padding: 9px 14px; font-size: 12px; font-weight: 600; color: #334155; cursor: pointer; display: flex; justify-content: space-between; align-items: center; user-select: none; list-style: none; }}
    .guide-summary::-webkit-details-marker {{ display: none; }}
    .guide-summary:hover {{ background: rgba(255, 255, 255, 0.4); }}
    .guide-content {{ padding: 10px 14px 12px 14px; border-top: 1px solid {THEME['border']}; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; background: rgba(255, 255, 255, 0.1); }}
    .guide-item {{ background: rgba(255, 255, 255, 0.5); border: 1px solid rgba(220, 220, 220, 0.5); border-radius: 8px; padding: 8px 10px; border-left-width: 3.5px; }}
    .guide-item.greed {{ border-left-color: #64748B; }}
    .guide-item.neutral {{ border-left-color: #D97706; }}
    .guide-item.fear {{ border-left-color: #DC2626; }}
    .guide-item-title {{ font-size: 11px; font-weight: 700; margin-bottom: 2px; }}
    .guide-item-desc {{ font-size: 11px; color: #64748B; line-height: 1.35; }}

    .scanner-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 18px; }}
    .scanner-panel {{ background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.015) 100%); border: 1px solid {THEME['border']}; border-top: 1px solid rgba(255, 255, 255, 0.3); border-radius: 12px; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); overflow: hidden; transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease; }}
    .scanner-panel:hover {{ transform: translateY(-3px); box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.2); border-color: rgba(200, 200, 200, 0.4); }}
    .scanner-panel-header {{ padding: 10px 14px; background: rgba(255, 255, 255, 0.03); border-bottom: 1px solid {THEME['border']}; display: flex; align-items: center; }}
    .market-badge {{ font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 5px; letter-spacing: 0.4px; line-height: 1; }}
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

    .sector-container {{ margin-top: 32px; }}
    .sector-header-title {{ font-size: 15px !important; font-weight: 700 !important; color: #0F172A !important; letter-spacing: -0.3px !important; }}
    .sector-header-desc {{ font-size: 12px !important; color: #64748B !important; margin-top: 2px !important; margin-bottom: 12px !important; }}
    .sector-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }}
    @media (max-width: 1024px) {{ .sector-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
    @media (max-width: 640px) {{ .sector-grid {{ grid-template-columns: repeat(2, 1fr); }} }}

    .sector-card {{ background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.015) 100%); border: 1px solid {THEME['border']}; border-radius: 10px; padding: 10px 12px; backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease; }}
    .sector-card:hover {{ transform: translateY(-2px); border-color: rgba(200, 200, 200, 0.4); }}
    .sector-card-top {{ display: flex; justify-content: space-between; align-items: center; }}
    .sector-card-name {{ font-size: 11px; font-weight: 700; color: {THEME['text_sub']}; opacity: 0.8; }}
    .sector-card-body {{ display: flex; align-items: baseline; justify-content: space-between; margin-top: 4px; }}
    .sector-card-score {{ font-size: 15px; font-weight: 800; color: {THEME['text_main']}; }}
    .sector-unit {{ font-size: 10px; font-weight: 700; margin-left: 1px; }}
    .sector-badge {{ font-size: 9.5px; font-weight: 800; padding: 2px 6px; border-radius: 4px; }}
    .sector-bar-bg {{ width: 100%; height: 3px; background: rgba(0, 0, 0, 0.06); border-radius: 2px; margin-top: 8px; overflow: hidden; }}
    .sector-bar-fill {{ height: 100%; border-radius: 2px; transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1); }}
    </style>
    """

    kospi_badge = '<span class="market-badge kospi">KOSPI</span>'
    kosdaq_badge = '<span class="market-badge kosdaq">KOSDAQ</span>'

    kospi_html = _render_column(kospi_badge, results.get("kospi", []), name_map)
    kosdaq_html = _render_column(kosdaq_badge, results.get("kosdaq", []), name_map)
    sector_html = _build_sector_grid_html(results, name_map)

    supply_bar_html = f"""
    <div class="supply-summary-bar">
        <div class="supply-title">장중 당일 수급 동향</div>
        <div class="supply-content-wrapper">
            <div class="supply-group">
                <span class="supply-market-tag">KOSPI</span>
                {kp_ssang_html}
                <div class="supply-sub-group">
                    <span class="supply-item-text">외국인 <span class="{_get_val_class(kp_f_val)}">{_fmt_num(kp_f_val)}</span></span>
                    <span class="supply-status-badge" style="color:{kp_eval['f_col']}; background:{kp_eval['f_bg']};">{kp_eval['f_txt']}</span>
                </div>
                <span class="supply-divider">|</span>
                <div class="supply-sub-group">
                    <span class="supply-item-text">기관 <span class="{_get_val_class(kp_i_val)}">{_fmt_num(kp_i_val)}</span></span>
                    <span class="supply-status-badge" style="color:{kp_eval['i_col']}; background:{kp_eval['i_bg']};">{kp_eval['i_txt']}</span>
                </div>
            </div>

            <div class="supply-group">
                <span class="supply-market-tag">KOSDAQ</span>
                {kd_ssang_html}
                <div class="supply-sub-group">
                    <span class="supply-item-text">외국인 <span class="{_get_val_class(kd_f_val)}">{_fmt_num(kd_f_val)}</span></span>
                    <span class="supply-status-badge" style="color:{kd_eval['f_col']}; background:{kd_eval['f_bg']};">{kd_eval['f_txt']}</span>
                </div>
                <span class="supply-divider">|</span>
                <div class="supply-sub-group">
                    <span class="supply-item-text">기관 <span class="{_get_val_class(kd_i_val)}">{_fmt_num(kd_i_val)}</span></span>
                    <span class="supply-status-badge" style="color:{kd_eval['i_col']}; background:{kd_eval['i_bg']};">{kd_eval['i_txt']}</span>
                </div>
            </div>
        </div>
    </div>
    """

    header_html = f"""
    {css}
    <div class="scanner-header-top">
        <div class="scanner-header-title">
            <span class="scanner-live-dot"></span>
            실시간 시장 공포·과매도 스캐너
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
    
    {supply_bar_html}

    <details class="guide-accordion">
        <summary class="guide-summary">
            <span><b>비명지수(0~100점) 투자 가이드 및 구간별 의미</b></span>
            <span style="font-size:10px; opacity:0.6;">접기/열기</span>
        </summary>
        <div class="guide-content">
            <div class="guide-item greed">
                <div class="guide-item-title" style="color:#64748B;">0 ~ 44점 | 탐욕 / 안정</div>
                <div class="guide-item-desc">군중 과열 심리 단계. 추격 매수를 자제하고 이익 실현 및 리스크를 관리하는 구간입니다.</div>
            </div>
            <div class="guide-item neutral">
                <div class="guide-item-title" style="color:#D97706;">45 ~ 64점 | 중립 / 관망</div>
                <div class="guide-item-desc">뚜렷한 방향성이 없는 상태. 수급 전환 및 기술적 지지 여부를 관망하는 구간입니다.</div>
            </div>
            <div class="guide-item fear">
                <div class="guide-item-title" style="color:#DC2626;">65 ~ 100점 | 과매도 / 역발상 매수</div>
                <div class="guide-item-desc">투매 및 비이성적 공포 확산. 분할 매수 진입 시 기대 승률이 가장 높은 타점입니다.</div>
            </div>
        </div>
    </details>

    <div class="scanner-grid">{kospi_html}{kosdaq_html}</div>
    {sector_html}
    """

    html_block(header_html)
