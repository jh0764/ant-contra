import streamlit as st
from urllib.parse import quote
from constants import THEME, PRICE_COLOR
from ui.common import html_block

def _render_card(r, name):
    p_color = PRICE_COLOR["up"] if r["change_pct"] >= 0 else PRICE_COLOR["down"]
    arrow = "▲" if r["change_pct"] >= 0 else "▼"
    score_color = "#DC2626" if r["score"] >= 65 else "#CA8A04" if r["score"] >= 45 else THEME['text_sub']
    stock_qp = quote(f"{name} ({r['code']})", safe="")
    return (
        f'<a href="?stock={stock_qp}" target="_self" style="text-decoration:none; display:block; margin-bottom:6px;">'
        f'<div style="background:{THEME["surface"]}; border:1px solid {THEME["border"]}; border-radius:10px; padding:8px 12px; display:flex; justify-content:space-between; align-items:center;">'
        f'<div style="display:flex; align-items:center; gap:8px; min-width:0;">'
        f'<span style="font-size:13.5px; font-weight:700; color:{THEME["text_main"]}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{name}</span>'
        f'<span style="font-size:10.5px; color:{THEME["text_sub"]}; white-space:nowrap;">{r["code"]}</span>'
        f'</div>'
        f'<div style="display:flex; align-items:center; gap:10px; flex-shrink:0;">'
        f'<span style="font-size:12px; color:{p_color}; white-space:nowrap;">{arrow} {r["change_pct"]:+.2f}%</span>'
        f'<span style="font-size:14px; font-weight:800; color:{score_color};">{r["score"]}점</span>'
        f'</div>'
        f'</div>'
        f'</a>'
    )

def _render_column(title, results, krx_listing):
    name_map = dict(zip(krx_listing["Code"], krx_listing["Name"]))
    if not results:
        return f'<div><div style="font-size:13px; font-weight:800; color:{THEME["text_main"]}; margin-bottom:8px;">{title}</div><div style="font-size:11.5px; color:{THEME["text_sub"]};">스캔 결과 없음</div></div>'
    cards = "".join(_render_card(r, name_map.get(r["code"], r["code"])) for r in results)
    return f'<div><div style="font-size:13px; font-weight:800; color:{THEME["text_main"]}; margin-bottom:8px;">{title}</div>{cards}</div>'

def render_fear_scanner(results, krx_listing):
    st.markdown(f"<div style='font-size:16px; font-weight:800; color:{THEME['text_main']}; margin-bottom:2px;'>🔥 오늘의 공포 TOP 10</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:10.5px; color:{THEME['text_sub']}; margin-bottom:10px;'>주요 대형주 고정 유니버스 대상 스캔 결과입니다 (실시간 시가총액 순위 기준 아님)</div>", unsafe_allow_html=True)

    kospi_html = _render_column("🔵 KOSPI", results.get("kospi", []), krx_listing)
    kosdaq_html = _render_column("🟢 KOSDAQ", results.get("kosdaq", []), krx_listing)

    st.markdown(f"""
    <style>
    .scanner-grid {{
        display:grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap:20px;
    }}
    </style>
    <div class="scanner-grid">{kospi_html}{kosdaq_html}</div>
    """, unsafe_allow_html=True)