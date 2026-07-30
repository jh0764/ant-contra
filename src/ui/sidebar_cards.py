import streamlit as st
from constants import STATUS_STYLE, THEME
from ui.common import html_block
from ui.gauge import render_wave_gauge
from constants import STATUS_STYLE, THEME, PRICE_COLOR, ACCENT

def render_entry_card(entry):
    html_block(
            f"""<div style="background:{THEME['surface']}; border:1px solid {entry['color']};
                border-radius:10px; padding:14px 16px; margin:0 0 14px 0;">
            <div style="font-size:15px; font-weight:700; color:{entry['color']};
                margin-bottom:4px;">{entry['level']}</div>
            <div style="font-size:12px; color:{THEME['text_sub']}; margin-bottom:10px;">{entry['desc']}</div>
            <div style="background:{entry['color']}18; border-radius:6px; padding:8px 12px;
                font-size:12px; color:{entry['color']}; font-weight:700;">
                → {entry['action']}
            </div>
            </div>"""
        )

def render_gauge_and_tier(final_scream_score, scream_tier, score_delta=None):
    render_wave_gauge(final_scream_score)
    tier_label, tier_color, tier_desc = scream_tier

    delta_html = ""
    if score_delta is not None and score_delta != 0:
        d_color = "#DC2626" if score_delta > 0 else "#3182f6"
        d_arrow = "▲" if score_delta > 0 else "▼"
        delta_html = f'<div style="margin-top:4px;"><span style="font-size:11px; color:{d_color}; font-weight:700;">{d_arrow} 전일 대비 {abs(score_delta)}점</span></div>'
    elif score_delta == 0:
        delta_html = f'<div style="margin-top:4px;"><span style="font-size:11px; color:{THEME["text_sub"]};">전일과 동일</span></div>'

    html_block(f"""
<div style="text-align:center; background:{THEME['surface']}; border:1px solid {tier_color}33;
 border-radius:8px; padding:8px; margin:10px 0 10px 0;">
<span style="color:{tier_color}; font-size:15px; font-weight:700;">{tier_label}</span><br>
<span style="color:{THEME['text_sub']}; font-size:10.5px;">{tier_desc}</span>
{delta_html}
</div>
""")

def render_score_history_sparkline(history):
    if not history or len(history) < 2:
        return
    values = [h["score"] for h in history]
    dates = [h["date"] for h in history]
    vmin, vmax = min(values), max(values)
    vrange = (vmax - vmin) or 1
    width, height = 260, 40
    step = width / (len(values) - 1)
    points = " ".join(
        f"{i * step:.1f},{height - ((v - vmin) / vrange * height):.1f}"
        for i, v in enumerate(values)
    )
    html_block(f"""
<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; padding:10px 14px; margin:0 0 12px 0;">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
<span style="font-size:11.5px; color:{THEME['text_sub']}; font-weight:700;">최근 {len(values)}거래일 점수 추이</span>
<span style="font-size:10.5px; color:{THEME['text_sub']};">{dates[0]} ~ {dates[-1]}</span>
</div>
<svg width="100%" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="none">
<polyline points="{points}" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
</div>
""")

def render_score_metrics(community_raw, objective_score, weight_reduced=False):
    col1, col2 = st.columns(2)
    for col, label, value in [(col1, "커뮤니티", community_raw), (col2, "객관지표", objective_score)]:
        with col:
            html_block(f"""
<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; padding:12px; text-align:center;">
<div style="font-size:11.5px; color:{THEME['text_sub']}; margin-bottom:4px;">{label}</div>
<div style="font-size:24px; font-weight:800; color:{THEME['text_main']};">{int(value)}점</div>
</div>
""")
    if weight_reduced:
        st.markdown(f"""
        <div style="font-size:8px; color:{THEME['text_sub']}; margin-top:4px; line-height:1.3; word-break:keep-all;">
        ⚠️ 변동성 확대로 커뮤니티 지표가 최종 점수에 반영되는 비중이 자동 축소되었습니다
        </div>
        """, unsafe_allow_html=True)

def render_signal_summary(obj_indicators):
    # ── 종합 판정 카드 (게이지 바로 아래) ────────────────────────
    indicator_meta = [
        ("rsi",      "📈 RSI (14일)",      "가격"),
        ("bb",       "〰️ 볼린저 밴드",     "가격"),
        ("w52",      "📉 52주 신저가",     "가격"),
        ("drawdown", "📉 고점낙폭", "가격"),  # 신규
        ("trend",    "🪫 장기추세", "가격"),
        ("candle",   "🕯️ 캔들패턴", "가격"),
        ("volume",   "🔊 거래량",          "수급"),
        ("foreign",  "🌍 외국인",          "수급"),
        ("obv", "📊 OBV 다이버전스", "수급")
    ]
    green_count = sum(1 for k,_,_ in indicator_meta if obj_indicators.get(k,{}).get("status") == "green")
    total_count = len(indicator_meta)

    if green_count >= 5:
        vd_bg, vd_border = STATUS_STYLE["green"]["bg"], STATUS_STYLE["green"]["border"]
        vd_text = f"신호 {green_count}/{total_count}개 포착 — 강력 역발상 매수 구간"
    elif green_count >= 3:
        vd_bg, vd_border = STATUS_STYLE["yellow"]["bg"], STATUS_STYLE["yellow"]["border"]
        vd_text = f"신호 {green_count}/{total_count}개 포착 — 보수적 분할 접근"
    else:
        vd_bg, vd_border = THEME['surface'], THEME['border']
        vd_text = f"신호 {green_count}/{total_count}개 — 관망 및 예수금 대기"

    html_block(f"""
    <div style="background:{vd_bg}; border:2px solid {vd_border}; border-radius:10px; padding:12px 14px; margin:6px 0 14px 0;">
    <span style="font-size:12.5px; color:{THEME['text_main']}; font-weight:600;">{vd_text}</span>
    </div>
    """)

def render_fomo_panel(fomo_data):
    bar_width = min(100, int(fomo_data["score"]))
    bar_color = fomo_data["color"]
    html_block(
        f"""<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px;
            padding:12px 14px; margin:0 0 12px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-size:12px; font-weight:700; color:{THEME['text_main']};">개미 관심도 지수</span>
            <span style="font-size:20px; font-weight:800; color:{bar_color};">{int(fomo_data['score'])}점</span>
        </div>
        <div style="font-size:11px; color:{bar_color}; font-weight:600; margin-bottom:6px;">{fomo_data['label']}</div>
        <div style="background:{THEME['border']}; border-radius:6px; height:8px; margin-bottom:6px;">
            <div style="background:{bar_color}; width:{bar_width}%; height:8px; border-radius:6px;"></div>
        </div>
        <div style="font-size:10.5px; color:{THEME['text_sub']};">{fomo_data['desc']}</div>
        </div>"""
    )

def render_indicator_group(keys, obj_indicators, group_label=None, only_signaled=False):
    if group_label:
        st.markdown(
            f"<p style='font-size:11px; color:{THEME['text_sub']}; font-weight:700; margin:8px 0 4px 2px;'>{group_label}</p>",
            unsafe_allow_html=True
        )

    signaled_items, other_items = [], []
    for key, title in keys:
        ind = obj_indicators.get(key, {})
        status = ind.get("status", "yellow")
        (signaled_items if status == "green" else other_items).append((title, ind, status))

    def _render_card_html(title, ind, status, size="lg"):
        sty = STATUS_STYLE.get(status, STATUS_STYLE.get("yellow", {}))
        icon_char, _, title_text = title.partition(" ")
        if size == "lg":
            chip, pad, icon_fs, title_fs, label_fs, desc_fs, bar = "34px", "14px 16px 14px 18px", "16px", "12.5px", "13.5px", "11.5px", "4px"
        else:
            chip, pad, icon_fs, title_fs, label_fs, desc_fs, bar = "30px", "13px 15px 13px 17px", "14.5px", "11.5px", "12.5px", "11px", "4px"
            
        return f'<div style="background:{THEME["surface"]}; border:1px solid {THEME["border"]}; border-left:{bar} solid {sty["border"]}; border-radius:10px; padding:{pad}; margin-bottom:8px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">' \
               f'<div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">' \
               f'<div style="display:flex; align-items:center; gap:10px; min-width:0;">' \
               f'<span style="width:{chip}; height:{chip}; border-radius:9px; background:{sty["bg"]}; display:flex; align-items:center; justify-content:center; font-size:{icon_fs}; flex-shrink:0;">{icon_char}</span>' \
               f'<div style="min-width:0;">' \
               f'<div style="font-size:{title_fs}; font-weight:800; color:{sty["border"]}; margin-bottom:1px;">{title_text}</div>' \
               f'<div style="font-size:{label_fs}; color:{THEME["text_main"]}; font-weight:600;">{ind.get("label","—")}</div>' \
               f'</div></div>' \
               f'<span style="background:{sty["badge_bg"]}; color:{sty["badge_color"]}; font-size:10px; font-weight:700; padding:3px 10px; border-radius:20px; white-space:nowrap; flex-shrink:0;">{sty["badge_text"]}</span>' \
               f'</div>' \
               f'<div style="font-size:{desc_fs}; color:{THEME["text_sub"]}; margin-top:6px; padding-left:44px;">{ind.get("desc","—")}</div>' \
               f'</div>'

    # 1. 포착 신호
    if signaled_items:
        for title, ind, status in signaled_items:
            st.markdown(_render_card_html(title, ind, status, size="lg"), unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="background:{THEME["surface"]}; border:1px dashed {THEME["border"]}; border-radius:10px; padding:12px; text-align:center; color:{THEME["text_sub"]}; font-size:12px; margin-bottom:6px;">현재 탭에서 포착된 매수/역발상 신호가 없습니다.</div>',
            unsafe_allow_html=True
        )

    # 2. 중립 및 미포착 지표 (구조 변경 없이 안전하게 이징 수치만 연장)
    if other_items:
        red_n = sum(1 for _, _, s in other_items if s == "red")
        yellow_n = sum(1 for _, _, s in other_items if s == "yellow")
        
        red_style = STATUS_STYLE.get("red", {})
        yellow_style = STATUS_STYLE.get("yellow", {})

        badges_html = ""
        if red_n > 0:
            badges_html += f'<span style="background:{red_style.get("badge_bg", "#fee2e2")}; color:{red_style.get("badge_color", "#dc2626")}; width:18px; height:18px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:10.5px; font-weight:800; margin-left:4px;">{red_n}</span>'
        if yellow_n > 0:
            badges_html += f'<span style="background:{yellow_style.get("badge_bg", "#fef3c7")}; color:{yellow_style.get("badge_color", "#d97706")}; width:18px; height:18px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-size:10.5px; font-weight:800; margin-left:4px;">{yellow_n}</span>'

        other_cards_html = "".join(_render_card_html(t, i, s, size="sm") for t, i, s in other_items)

        chk_id = f"acc-toggle-{hash(group_label or 'default') & 0xffffffff}"

        accordion_html = f"""
        <style>
        .pure-acc-checkbox {{
            display: none !important;
        }}
        
        .pure-acc-label {{
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            padding: 12px 14px !important;
            background: {THEME['surface']} !important;
            border: 1px solid {THEME['border']} !important;
            border-radius: 10px !important;
            cursor: pointer !important;
            user-select: none !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
            margin-top: 6px !important;
            transition: background 0.2s ease, border-color 0.2s ease !important;
        }}
        .pure-acc-label:hover {{
            border-color: {THEME.get('text_sub', '#9ca3af')} !important;
        }}
        .pure-acc-title {{
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            color: {THEME['text_main']} !important;
        }}
        
        /* 화살표 회전 */
        .pure-acc-svg {{
            width: 16px;
            height: 16px;
            transition: transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        #{chk_id}:checked + .pure-acc-label .pure-acc-svg {{
            transform: rotate(180deg);
        }}
        
        /* 이전 코드의 max-height: 600px 유지 및 시간만 0.55s -> 0.75s 확장 */
        .pure-acc-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.75s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        #{chk_id}:checked ~ .pure-acc-content {{
            max-height: 600px;
            transition: max-height 0.75s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        
        /* 이전 코드 구조 그대로 유지하면서 페이드/이동 시간만 0.4s -> 0.6s 연장 */
        .pure-acc-inner {{
            padding-top: 8px;
            opacity: 0;
            transform: translateY(-10px);
            transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        #{chk_id}:checked ~ .pure-acc-content .pure-acc-inner {{
            opacity: 1;
            transform: translateY(0);
            transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.05s, transform 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.05s;
        }}
        </style>

        <div>
            <input type="checkbox" id="{chk_id}" class="pure-acc-checkbox" />
            <label for="{chk_id}" class="pure-acc-label">
                <div class="pure-acc-title">
                    <span>중립 및 미포착 지표</span>
                    {badges_html}
                </div>
                <svg class="pure-acc-svg" viewBox="0 0 24 24" fill="none" stroke="{THEME['text_sub']}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </label>
            <div class="pure-acc-content">
                <div class="pure-acc-inner">
                    {other_cards_html}
                </div>
            </div>
        </div>
        """
        st.markdown(accordion_html, unsafe_allow_html=True)

def render_risk_card(risk_levels):
    if not risk_levels:
        return
    stop_color = PRICE_COLOR['down']    # 파란색
    target_color = PRICE_COLOR['up']    # 빨간색
    verdict_color = {"우수": target_color, "양호": target_color, "미흡": stop_color, "산출불가": THEME['text_sub']}
    v_color = verdict_color.get(risk_levels["rr_verdict"], THEME['text_sub'])
    html_block(f"""
<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; padding:12px 14px; margin:0 0 12px 0;">
<div style="font-size:12px; font-weight:700; color:{THEME['text_main']}; margin-bottom:8px;">손익비 타점 (R:R)</div>
<div style="display:flex; justify-content:space-between; font-size:11.5px; color:{THEME['text_sub']}; margin-bottom:3px;">
<span>손절가</span><span style="color:{stop_color}; font-weight:700;">{risk_levels['stop_loss']:,}원 (-{risk_levels['risk_pct']}%)</span>
</div>
<div style="display:flex; justify-content:space-between; font-size:11.5px; color:{THEME['text_sub']}; margin-bottom:3px;">
<span>1차 목표가</span><span style="color:{target_color}; font-weight:700;">{risk_levels['target1']:,}원 (+{risk_levels['reward_pct']}%)</span>
</div>
<div style="display:flex; justify-content:space-between; font-size:11.5px; color:{THEME['text_sub']}; margin-bottom:6px;">
<span>2차 목표가</span><span style="color:{THEME['text_main']};">{risk_levels['target2']:,}원</span>
</div>
<div style="background:{v_color}18; border-radius:6px; padding:5px 10px; text-align:center;">
<span style="color:{v_color}; font-weight:700; font-size:12px;">R:R {risk_levels['rr_ratio']} — {risk_levels['rr_verdict']}</span>
</div>
</div>
""")