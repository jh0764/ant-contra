import hashlib
import streamlit as st
from constants import TICKER_BADGE_COLORS, THEME
from ui.common import html_block

def render_company_header(company_name, ticker_code, sector="—"):
    idx = int(hashlib.md5(ticker_code.encode()).hexdigest(), 16) % len(TICKER_BADGE_COLORS)
    color = TICKER_BADGE_COLORS[idx]
    initial = company_name[0]

    html_block(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
      <div style="width:44px; height:44px; border-radius:50%; background:{color};
           display:flex; align-items:center; justify-content:center;
           color:white; font-weight:700; font-size:18px; flex-shrink:0;">{initial}</div>
      <div>
        <div style="font-size:19px; font-weight:800; color:{THEME['text_main']};">{company_name}</div>
        <div style="font-size:12px; color:{THEME['text_sub']};">{ticker_code} · {sector}</div>
      </div>
    </div>
    """)