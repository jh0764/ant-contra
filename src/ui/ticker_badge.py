import hashlib
import streamlit as st
from constants import TICKER_BADGE_COLORS, THEME
from ui.common import html_block

def render_company_header(company_name, ticker_code, sector="—"):
    code_str = str(ticker_code).zfill(6)
    
    idx = int(hashlib.md5(code_str.encode()).hexdigest(), 16) % len(TICKER_BADGE_COLORS)
    color = TICKER_BADGE_COLORS[idx]
    initial = company_name[0] if company_name else "S"

    # 토스 원본 이미지 URL (리사이징 서버 프록시 차단 방지)
    toss_logo_url = f"https://static.toss.im/png-icons/securities/icn-sec-fill-{code_str}.png"

    html_block(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
      <div style="position:relative; width:44px; height:44px; border-radius:50%; background:{color};
           display:flex; align-items:center; justify-content:center;
           color:white; font-weight:700; font-size:18px; flex-shrink:0; overflow:hidden;">
        
        <!-- 로딩 실패 시 태그 자체를 remove() 하여 엑박 아이콘 흔적을 완전 제거 -->
        <img src="{toss_logo_url}" 
             onerror="this.onerror=null; this.remove();" 
             style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; z-index:2;" />
             
        <span style="position:relative; z-index:1;">{initial}</span>
      </div>

      <div>
        <div style="font-size:19px; font-weight:800; color:{THEME['text_main']};">{company_name}</div>
        <div style="font-size:12px; color:{THEME['text_sub']};">{code_str} · {sector}</div>
      </div>
    </div>
    """)