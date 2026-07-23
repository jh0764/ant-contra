import streamlit as st
from core.market_index import get_market_index_series
from ui.common import html_block
from constants import THEME, PRICE_COLOR

def _build_sparkline_svg(series, color, width=100, height=32):
    values = series.tail(30).tolist()
    if len(values) < 2:
        return ""
    vmin, vmax = min(values), max(values)
    vrange = (vmax - vmin) or 1
    step = width / (len(values) - 1)
    points = [f"{i*step:.1f},{height - ((v - vmin) / vrange * height):.1f}" for i, v in enumerate(values)]
    return f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'

def render_index_ticker():
    cols = st.columns(2)
    for col, is_kosdaq, label in [(cols[0], False, "코스피"), (cols[1], True, "코스닥")]:
        series = get_market_index_series(is_kosdaq)
        with col:
            if series is None or len(series) < 2:
                html_block(f"""
<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; padding:10px 14px;">
<span style="font-size:11.5px; color:{THEME['text_sub']};">{label} — 데이터 불러오기 실패</span>
</div>
""")
                continue
            current = float(series.iloc[-1])
            prev = float(series.iloc[-2])
            change_pct = (current - prev) / prev * 100
            p_color = PRICE_COLOR["up"] if change_pct >= 0 else PRICE_COLOR["down"]
            arrow = "▲" if change_pct >= 0 else "▼"
            spark = _build_sparkline_svg(series, p_color)
            html_block(f"""
<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; padding:10px 14px; display:flex; align-items:center; justify-content:space-between; gap:10px;">
<div>
<div style="font-size:11.5px; color:{THEME['text_sub']}; margin-bottom:2px;">{label}</div>
<div style="font-size:16px; font-weight:800; color:{THEME['text_main']};">{current:,.2f}</div>
<div style="font-size:11px; color:{p_color}; font-weight:700;">{arrow} {change_pct:+.2f}%</div>
</div>
<svg width="100" height="32" viewBox="0 0 100 32">{spark}</svg>
</div>
""")