import streamlit as st
from constants import PRICE_COLOR, THEME, SPACING
from ui.common import html_block

def render_price_info(current_price, change_pct, ant_refund_line, fib, volatility_warning):
    is_up = change_pct >= 0
    p_color = PRICE_COLOR["up"] if is_up else PRICE_COLOR["down"]
    p_bg = "#fee2e2" if is_up else "#dbeafe"
    arrow = "▲" if is_up else "▼"
    vwap_status = "손실 구간" if current_price < ant_refund_line else "수익 구간"

    st.markdown(f"""
    <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:{SPACING};">
      <span style="font-size:32px; font-weight:800; color:{p_color};">{current_price:,}원</span>
      <span style="background:{p_bg}; color:{p_color}; font-weight:700; font-size:13px;
            padding:3px 10px; border-radius:6px;">{arrow} {change_pct:+.2f}%</span>
    </div>
    <div style="font-size:12.5px; color:{THEME['text_sub']}; margin-bottom:10px;">
      개미 평단 추정선 <b style="color:{THEME['text_main']};">{ant_refund_line:,}원</b> — {vwap_status}
    </div>
    """, unsafe_allow_html=True)

    if fib:
        pct, price, status = fib
        gap_pct = (current_price - price) / price * 100
        pct_color = PRICE_COLOR["up"] if gap_pct >= 0 else PRICE_COLOR["down"]
        fib_border = pct_color
        fib_msg = "현재가가 이 라인 위에 있어 '지지선' 역할을 하고 있어요." if status == "지지" \
            else "현재가가 이 라인 아래로 내려가 '저항선'으로 바뀐 상태예요."
        html_block(f"""
        <div style="background:{THEME['surface']}; border:1px solid {fib_border}55; border-radius:8px; padding:10px 14px; margin:{SPACING} 0;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
        <span style="font-size:12.5px; color:{THEME['text_main']}; font-weight:700;">피보나치 되돌림 {pct*100:.1f}%</span>
        <span style="font-size:11.5px; font-weight:700; color:{pct_color};">{status} ({gap_pct:+.1f}%)</span>
        </div>
        <div style="font-size:11px; color:{THEME['text_sub']}; margin-top:4px;">
        기준가 <b style="color:{THEME['text_main']};">{price:,.0f}원</b> — 52주 고점·저점 사이 되돌림 구간. {fib_msg}
        </div>
        </div>
        """)

    if volatility_warning:
        st.warning(volatility_warning)

def render_community_tab(naver_posts, ai_reason=None):
    st.markdown(f"<p style='font-size:14px; font-weight:700; color:{THEME['text_main']};'>실시간 주주 비명소리</p>", unsafe_allow_html=True)
    if ai_reason:
        st.markdown(
            f"<p style='font-size:11.5px; color:{THEME['text_sub']}; margin-top:-4px; margin-bottom:8px;'>{ai_reason}</p>",
            unsafe_allow_html=True
        )
    cols_post = st.columns(2)
    for idx, post in enumerate(naver_posts[:8], 0):
        likes = post['likes']
        badge_color = "#16a34a" if likes >= 20 else "#ca8a04" if likes >= 5 else THEME['text_sub']
        with cols_post[idx % 2]:
            st.markdown(
                f"""<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:8px; padding:9px 11px;
                    margin-bottom:8px; border-left:3px solid {badge_color};">
                <div style="font-size:12px; color:{THEME['text_main']}; line-height:1.4; margin-bottom:4px;">{post['title']}</div>
                <div style="font-size:10.5px; color:{THEME['text_sub']};">👍 {post['likes']} &nbsp;·&nbsp; 👀 {post['views']}</div>
                </div>""",
                unsafe_allow_html=True
            )

def render_fundamental_stats(fundamentals):
    items = [
        ("시가총액", fundamentals["market_cap"]), ("PER", fundamentals["per"]),
        ("PBR", fundamentals["pbr"]), ("EPS", fundamentals["eps"]),
        ("배당수익률", fundamentals["dividend_yield"]),
    ]
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        with col:
            html_block(f"""
<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:8px; padding:10px 8px; text-align:center; height:72px; display:flex; flex-direction:column; justify-content:center;">
<div style="font-size:11px; color:{THEME['text_sub']}; margin-bottom:3px;">{label}</div>
<div style="font-size:12px; font-weight:700; color:{THEME['text_main']}; white-space:normal; word-break:keep-all; line-height:1.3;">{value}</div>
</div>
""")