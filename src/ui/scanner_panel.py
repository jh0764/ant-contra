import streamlit as st
from constants import THEME, PRICE_COLOR
from ui.common import html_block

def render_fear_scanner(results, krx_listing):
    st.markdown(f"<div style='font-size:16px; font-weight:800; color:{THEME['text_main']}; margin-bottom:10px;'>🔥 오늘의 공포 TOP {len(results)}</div>", unsafe_allow_html=True)

    if not results:
        st.info("스캔 결과를 불러오지 못했습니다.")
        return

    name_map = dict(zip(krx_listing["Code"], krx_listing["Name"]))

    for i, r in enumerate(results, 1):
        name = name_map.get(r["code"], r["code"])
        p_color = PRICE_COLOR["up"] if r["change_pct"] >= 0 else PRICE_COLOR["down"]
        arrow = "▲" if r["change_pct"] >= 0 else "▼"
        score_color = "#DC2626" if r["score"] >= 65 else "#CA8A04" if r["score"] >= 45 else THEME['text_sub']

        col1, col2 = st.columns([5, 1])
        with col1:
            html_block(f"""
<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; padding:10px 14px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
<div style="display:flex; align-items:center; gap:10px;">
<span style="font-size:12px; color:{THEME['text_sub']}; width:18px;">{i}</span>
<span style="font-size:13.5px; font-weight:700; color:{THEME['text_main']};">{name}</span>
<span style="font-size:11px; color:{THEME['text_sub']};">{r['code']}</span>
</div>
<div style="display:flex; align-items:center; gap:14px;">
<span style="font-size:12.5px; color:{p_color};">{arrow} {r['change_pct']:+.2f}%</span>
<span style="font-size:15px; font-weight:800; color:{score_color};">{r['score']}점</span>
</div>
</div>
""")
        with col2:
            if st.button("보기", key=f"scan_{r['code']}"):
                st.session_state["last_selected"] = f"{name} ({r['code']})"
                st.session_state["dashboard_ready"] = True
                st.rerun()