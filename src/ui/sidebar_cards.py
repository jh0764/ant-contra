import streamlit as st
from constants import STATUS_STYLE, THEME
from ui.common import html_block
from ui.gauge import render_wave_gauge

def render_entry_card(entry):
    html_block(
            f"""<div style="background:{THEME['surface']}; border:2px solid {entry['color']}55;
                border-radius:10px; padding:14px 16px; margin:0 0 14px 0;">
            <div style="font-size:15px; font-weight:700; color:{entry['color']};
                margin-bottom:4px;">{entry['level']}</div>
            <div style="font-size:11.5px; color:{THEME['text_sub']}; margin-bottom:6px;">{entry['desc']}</div>
            <div style="background:{entry['color']}18; border-radius:6px; padding:6px 10px;
                font-size:12px; color:{entry['color']}; font-weight:600;">
                → {entry['action']}
            </div>
            </div>"""
        )
    
def render_gauge_and_tier(final_scream_score, scream_tier):
    render_wave_gauge(final_scream_score)
    tier_label, tier_color, tier_desc = scream_tier
    html_block(f"""
<div style="text-align:center; background:{THEME['surface']}; border:1px solid {tier_color}33;
 border-radius:8px; padding:8px; margin:10px 0 10px 0;">
<span style="color:{tier_color}; font-size:15px; font-weight:700;">{tier_label}</span><br>
<span style="color:{THEME['text_sub']}; font-size:10.5px;">{tier_desc}</span>
</div>
""")

def render_score_metrics(community_raw, objective_score):
    col1, col2 = st.columns(2)
    for col, label, value in [(col1, "커뮤니티", community_raw), (col2, "객관지표", objective_score)]:
        with col:
            html_block(f"""
<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; padding:12px; text-align:center;">
<div style="font-size:11.5px; color:{THEME['text_sub']}; margin-bottom:4px;">{label}</div>
<div style="font-size:24px; font-weight:800; color:{THEME['text_main']};">{int(value)}점</div>
</div>
""")

def render_signal_summary(obj_indicators):
    # ── 종합 판정 카드 (게이지 바로 아래) ────────────────────────
    indicator_meta = [
        ("rsi",      "📈 RSI (14일)",      "가격"),
        ("bb",       "〰️ 볼린저 밴드",     "가격"),
        ("w52",      "📉 52주 신저가",     "가격"),
        ("drawdown", "📉 고점낙폭", "가격"),  # 신규
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

def render_indicator_group(keys, obj_indicators, group_label=None):
    if group_label:
        st.markdown(f"<p style='font-size:11px; color:{THEME['text_sub']}; font-weight:700; margin:8px 0 4px 2px;'>{group_label}</p>", unsafe_allow_html=True)
    for key, title in keys:
        ind = obj_indicators.get(key, {})
        sty = STATUS_STYLE[ind.get("status", "yellow")]
        st.markdown(
            f"""<div style="background:{sty['bg']}; border:2px solid {sty['border']}; border-left:5px solid {sty['border']};
                 border-radius:8px; padding:10px 12px; margin-bottom:6px;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                <div style="font-size:12px; color:{THEME['text_main']};">{title}</div>
                <span style="background:{sty['badge_bg']}; color:{sty['badge_color']}; font-size:10px;
                       padding:1px 7px; border-radius:20px; font-weight:600; white-space:nowrap;">{sty['badge_text']}</span>
              </div>
              <div style="font-size:12px; color:{THEME['text_main']}; font-weight:600;">{ind.get('label','—')}</div>
              <div style="font-size:10.5px; color:{THEME['text_sub']};">{ind.get('desc','—')}</div>
            </div>""",
            unsafe_allow_html=True
        )
