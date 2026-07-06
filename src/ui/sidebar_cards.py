import streamlit as st
import plotly.graph_objects as go
from constants import STATUS_STYLE


def render_entry_card(entry):
    st.markdown(
            f"""<div style="background:#0f172a; border:2px solid {entry['color']}55;
                border-radius:10px; padding:14px 16px; margin:0 0 14px 0;">
            <div style="font-size:15px; font-weight:700; color:{entry['color']};
                margin-bottom:4px;">{entry['level']}</div>
            <div style="font-size:11.5px; color:#94a3b8; margin-bottom:6px;">{entry['desc']}</div>
            <div style="background:{entry['color']}22; border-radius:6px; padding:6px 10px;
                font-size:12px; color:{entry['color']}; font-weight:600;">
                → {entry['action']}
            </div>
            </div>""",
            unsafe_allow_html=True
        )
    
def render_gauge_and_tier(final_scream_score, scream_tier):
    # ── 통합 비명 지수 게이지 ─────────────────────────────────────
    # 점수별 게이지 색상
    if final_scream_score >= 85:
        gauge_color, number_color = "#dc2626", "#ff4444"
    elif final_scream_score >= 70:
        gauge_color, number_color = "#ea580c", "#fb923c"
    elif final_scream_score >= 55:
        gauge_color, number_color = "#ca8a04", "#fbbf24"
    elif final_scream_score >= 35:
        gauge_color, number_color = "#475569", "#94a3b8"
    else:
        gauge_color, number_color = "#16a34a", "#4ade80"

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=final_scream_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "통합 비명 지수", 'font': {'size': 14, 'color': '#e2e8f0'}},
        number={'font': {'size': 48, 'color': number_color}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#475569",
                    'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': gauge_color},
            'bgcolor': "#0f172a",
            'borderwidth': 1,
            'bordercolor': "#1e293b",
            'steps': [
                {'range': [0,  35], 'color': '#052e16'},   # 탐욕 — 다크그린
                {'range': [35, 55], 'color': '#1e293b'},   # 중립 — 다크슬레이트
                {'range': [55, 70], 'color': '#2d1f00'},   # 공포진입 — 다크옐로                    {'range': [70, 85], 'color': '#2d0f00'},   # 공포 — 다크오렌지
                {'range': [85,100], 'color': '#1f0000'},   # 극단공포 — 다크레드
            ],
            'threshold': {'line': {'color': gauge_color, 'width': 3},
                        'thickness': 0.75, 'value': final_scream_score}
        }
    ))
    fig_gauge.update_layout(
        height=210,
        margin=dict(l=15, r=15, t=35, b=5),
        font={'family': "Malgun Gothic"},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    tier_label, tier_color, tier_desc = scream_tier
    st.markdown(
        f"""<div style="text-align:center; background:#0f172a; border:1px solid {tier_color}33;
            border-radius:8px; padding:8px; margin:-4px 0 10px 0;">
        <span style="color:{tier_color}; font-size:15px; font-weight:700;">{tier_label}</span><br>
        <span style="color:#94a3b8; font-size:10.5px;">{tier_desc}</span>
        </div>""",
        unsafe_allow_html=True
    )

def render_score_metrics(community_raw, objective_score):
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.metric("💬 커뮤니티", f"{int(community_raw)}점", help="네이버 여론")
    with g_col2:
        st.metric("📐 객관지표", f"{int(objective_score)}점", help="RSI·수급 등")

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

    if green_count >= 4:
        vd_bg, vd_border, vd_icon = "#0d2b1a", "#22c55e", "🔥"
        vd_text = f"신호 {green_count}/{total_count}개 포착 — 강력 역발상 매수 구간"
    elif green_count >= 2:
        vd_bg, vd_border, vd_icon = "#2b2200", "#eab308", "⚡️"
        vd_text = f"신호 {green_count}/{total_count}개 포착 — 보수적 분할 접근"
    else:
        vd_bg, vd_border, vd_icon = "#1e293b", "#475569", "💤"
        vd_text = f"신호 {green_count}/{total_count}개 — 관망 및 예수금 대기"

    st.markdown(
        f"""<div style="background:{vd_bg}; border:2px solid {vd_border}; border-radius:10px;
             padding:12px 14px; margin:6px 0 14px 0; display:flex; align-items:center; gap:10px;">
          <span style="font-size:20px;">{vd_icon}</span>
          <span style="font-size:12.5px; color:#f1f5f9; font-weight:600; line-height:1.4;">{vd_text}</span>
        </div>""",
        unsafe_allow_html=True
    )

def render_fomo_panel(fomo_data):
    bar_width = min(100, int(fomo_data["score"]))
    bar_color = fomo_data["color"]
    st.markdown(
        f"""<div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px;
            padding:12px 14px; margin:0 0 12px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-size:12px; font-weight:700; color:#e2e8f0;">🎯 개미 관심도 지수</span>
            <span style="font-size:20px; font-weight:800; color:{bar_color};">{int(fomo_data['score'])}점</span>
        </div>
        <div style="font-size:11px; color:{bar_color}; font-weight:600; margin-bottom:6px;">{fomo_data['label']}</div>
        <div style="background:#1e293b; border-radius:6px; height:8px; margin-bottom:6px;">
            <div style="background:{bar_color}; width:{bar_width}%; height:8px; border-radius:6px;"></div>
        </div>
        <div style="font-size:10.5px; color:#94a3b8;">{fomo_data['desc']}</div>
        <div style="font-size:10px; color:#475569; margin-top:4px;">
            📌 관심도 높음+공포 높음 = 반등 강도 ↑ &nbsp;|&nbsp; 관심도 낮음+공포 높음 = 바닥 탐색 중
        </div>
        </div>""",
        unsafe_allow_html=True
    )

def render_indicator_group(group_label, keys, obj_indicators):
    st.markdown(f"<p style='font-size:11px; color:#64748b; font-weight:700; margin:8px 0 4px 2px; letter-spacing:0.5px;'>▸ {group_label}</p>", unsafe_allow_html=True)
    for key, title in keys:
        ind = obj_indicators.get(key, {})
        sty = STATUS_STYLE[ind.get("status", "yellow")]
        st.markdown(
            f"""<div style="background:{sty['bg']}; border:1px solid {sty['border']};
                 border-radius:8px; padding:10px 12px; margin-bottom:6px;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                <span style="font-size:12px; font-weight:700; color:#e2e8f0;">{title}</span>
                <span style="background:{sty['badge_bg']}; color:white; font-size:10px;
                       padding:1px 7px; border-radius:20px; font-weight:600; white-space:nowrap;">{sty['badge_text']}</span>
              </div>
              <div style="font-size:12px; color:#f1f5f9; font-weight:600; margin-bottom:1px;">{ind.get('label','—')}</div>
              <div style="font-size:10.5px; color:#94a3b8;">{ind.get('desc','—')}</div>
            </div>""",
            unsafe_allow_html=True
        )
