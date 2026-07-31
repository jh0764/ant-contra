import streamlit as st
from constants import STATUS_STYLE, THEME, PRICE_COLOR, ACCENT
from ui.common import html_block
from ui.gauge import render_wave_gauge

def render_entry_card(entry):
    """2. 매매 전략 판단 (좌측 포인트 바 + 은은한 그림자 적용)"""
    level = entry.get("level", "대기")
    desc = entry.get("desc", "")
    action = entry.get("action", "")

    short_desc = desc.split('.')[0] if '.' in desc else desc

    html_block(f"""
    <div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-left:4px solid #d97706; border-radius:10px; padding:14px; margin:8px 0; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-size:11px; color:{THEME['text_sub']}; font-weight:700; letter-spacing:-0.2px;">매매 전략</span>
            <span style="background:#fff7ed; color:#c2410c; font-size:10.5px; font-weight:800; padding:2px 7px; border-radius:4px; border:1px solid #ffedd5;">{level}</span>
        </div>
        <div style="font-size:13.5px; font-weight:800; color:{THEME['text_main']}; margin-bottom:6px; letter-spacing:-0.3px; line-height:1.3;">
            {action}
        </div>
        <div style="font-size:11px; color:{THEME['text_sub']}; font-weight:500; line-height:1.4;">
            {short_desc}
        </div>
    </div>
    """)


def render_risk_card(risk_levels):
    """3. 손익비 타점 (가격을 여유 있게 보여주는 깔끔한 수평 리스트 레이아웃)"""
    if not risk_levels:
        return
        
    stop_color = PRICE_COLOR['down']
    target_color = PRICE_COLOR['up']
    verdict_color = {"우수": target_color, "양호": target_color, "미흡": stop_color, "산출불가": THEME['text_sub']}
    v_color = verdict_color.get(risk_levels["rr_verdict"], THEME['text_sub'])

    # 가격 크기에 따른 동적 폰트 크기 설정 (100만 원 이상일 때 자릿수 답답함 방지)
    max_val = max(risk_levels.get('stop_loss', 0), risk_levels.get('target1', 0), risk_levels.get('target2', 0))
    val_font_size = "12px" if max_val >= 1_000_000 else "12.5px"

    html_block(f"""
    <div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; padding:12px 14px; margin-bottom:8px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
        <!-- 헤더 -->
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; padding-bottom:6px; border-bottom:1px solid {THEME['border']};">
            <span style="font-size:11px; color:{THEME['text_sub']}; font-weight:700;">손익비 타점</span>
            <span style="font-size:12px; font-weight:800; color:{v_color};">
                R:R {risk_levels['rr_ratio']} <span style="font-size:10.5px; font-weight:600; color:{THEME['text_sub']};">({risk_levels['rr_verdict']})</span>
            </span>
        </div>
        
        <!-- 행 단위 가격 리스트 (자릿수 길이에 구애받지 않음) -->
        <div style="display:flex; flex-direction:column; gap:6px;">
            <!-- 손절가 -->
            <div style="display:flex; justify-content:space-between; align-items:center; background:{THEME['bg']}; padding:6px 10px; border-radius:6px;">
                <span style="font-size:11px; color:{THEME['text_sub']}; font-weight:600; width:55px;">손절가</span>
                <span style="font-size:{val_font_size}; font-weight:800; color:{stop_color};">{risk_levels['stop_loss']:,}원</span>
                <span style="font-size:10.5px; font-weight:700; color:{stop_color}; text-align:right; width:50px;">-{risk_levels['risk_pct']}%</span>
            </div>
            
            <!-- 1차 목표가 -->
            <div style="display:flex; justify-content:space-between; align-items:center; background:{THEME['bg']}; padding:6px 10px; border-radius:6px;">
                <span style="font-size:11px; color:{THEME['text_sub']}; font-weight:600; width:55px;">1차 목표</span>
                <span style="font-size:{val_font_size}; font-weight:800; color:{target_color};">{risk_levels['target1']:,}원</span>
                <span style="font-size:10.5px; font-weight:700; color:{target_color}; text-align:right; width:50px;">+{risk_levels['reward_pct']}%</span>
            </div>
            
            <!-- 2차 목표가 -->
            <div style="display:flex; justify-content:space-between; align-items:center; background:{THEME['bg']}; padding:6px 10px; border-radius:6px;">
                <span style="font-size:11px; color:{THEME['text_sub']}; font-weight:600; width:55px;">2차 목표</span>
                <span style="font-size:{val_font_size}; font-weight:800; color:{THEME['text_main']};">{risk_levels['target2']:,}원</span>
                <span style="font-size:10.5px; font-weight:600; color:{THEME['text_sub']}; text-align:right; width:50px;">—</span>
            </div>
        </div>
    </div>
    """)
    
def render_gauge_and_tier(final_scream_score, scream_tier, score_delta=None):
    """1. 통합 심리 지수 (슬림화)"""
    tier_label, tier_color, tier_desc = scream_tier

    diff_text = "전일과 동일"
    if score_delta is not None and score_delta != 0:
        d_arrow = "▲" if score_delta > 0 else "▼"
        diff_text = f"{d_arrow} 전일 대비 {abs(score_delta)}점"

    render_wave_gauge(
        score=final_scream_score,
        label_top="통합 비명 지수",
        comment_text=tier_desc,
        diff_text=diff_text
    )
    
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
    """4. 세부 점수 및 변동성 주의 문구 (디자인 보완)"""
    html_block(f"""
    <div style="display:flex; gap:8px; margin-bottom:8px;">
        <div style="flex:1; background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; padding:10px 12px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
            <span style="font-size:11px; color:{THEME['text_sub']}; font-weight:600;">커뮤니티</span>
            <span style="font-size:15px; font-weight:800; color:{THEME['text_main']};">{int(community_raw)}점</span>
        </div>
        <div style="flex:1; background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; padding:10px 12px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
            <span style="font-size:11px; color:{THEME['text_sub']}; font-weight:600;">객관지표</span>
            <span style="font-size:15px; font-weight:800; color:{THEME['text_main']};">{int(objective_score)}점</span>
        </div>
    </div>
    """)
    if weight_reduced:
        html_block(f"""
        <div style="font-size:10.5px; color:#b45309; background:#fffbebe6; border:1px solid #fef3c7; border-radius:8px; padding:7px 10px; margin-bottom:8px; text-align:center; font-weight:600; display:flex; align-items:center; justify-content:center; gap:4px;">
            <span>⚠️</span> <span>변동성 확대로 커뮤니티 지표 비중 축소 적용 중</span>
        </div>
        """)


def render_signal_summary(obj_indicators):
    """5. 매수 신호 요약 (입체감 있는 배지 스타일)"""
    indicator_meta = [
        ("rsi", "RSI"), ("bb", "볼린저"), ("w52", "신저가"),
        ("drawdown", "낙폭"), ("trend", "추세"), ("candle", "캔들"),
        ("volume", "거래량"), ("foreign", "외국인"), ("obv", "OBV")
    ]
    green_count = sum(1 for k,_ in indicator_meta if obj_indicators.get(k,{}).get("status") == "green")
    total_count = len(indicator_meta)

    if green_count >= 5:
        vd_bg, vd_border, vd_color = "#f0fdf4", "#bbf7d0", "#15803d"
        st_text = "강력 역발상"
    elif green_count >= 3:
        vd_bg, vd_border, vd_color = "#fffbeb", "#fef08a", "#b45309"
        st_text = "보수적 접근"
    else:
        vd_bg, vd_border, vd_color = THEME['bg'], THEME['border'], THEME['text_sub']
        st_text = "관망 권장"

    html_block(f"""
    <div style="background:{vd_bg}; border:1px solid {vd_border}; border-radius:10px; padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 2px rgba(0,0,0,0.02);">
        <span style="font-size:11.5px; color:{vd_color}; font-weight:700;">매수 신호 포착</span>
        <span style="font-size:12px; color:{vd_color}; font-weight:800;">{green_count}/{total_count}개 <span style="font-size:10px; font-weight:600; opacity:0.85;">({st_text})</span></span>
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

    if signaled_items:
        for title, ind, status in signaled_items:
            st.markdown(_render_card_html(title, ind, status, size="lg"), unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="background:{THEME["surface"]}; border:1px dashed {THEME["border"]}; border-radius:10px; padding:12px; text-align:center; color:{THEME["text_sub"]}; font-size:12px; margin-bottom:6px;">현재 탭에서 포착된 매수/역발상 신호가 없습니다.</div>',
            unsafe_allow_html=True
        )

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
        
        .pure-acc-svg {{
            width: 16px;
            height: 16px;
            transition: transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        #{chk_id}:checked + .pure-acc-label .pure-acc-svg {{
            transform: rotate(180deg);
        }}
        
        .pure-acc-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.75s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        #{chk_id}:checked ~ .pure-acc-content {{
            max-height: 600px;
            transition: max-height 0.75s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        
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