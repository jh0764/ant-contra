import streamlit as st

def render_price_info(current_price, change_pct, ant_refund_line, fib, volatility_warning):
    up_down_emoji = "🔺" if change_pct >= 0 else "🔻"
    vwap_status = "🔴 개미 대부분 손실 구간" if current_price < ant_refund_line else "🟢 개미 대부분 수익 구간"
    vwap_label  = f"개미 평단 추정선: **{ant_refund_line:,}원** {vwap_status}"
    st.info(f"현재 주가: **{current_price:,}원** ({up_down_emoji} {change_pct:+.2f}%) | {vwap_label}")

    if fib:
        pct, price, status = fib
        gap_pct = (current_price - price) / price * 100
        fib_color = "#22c55e" if status == "지지" else "#ef4444"
        fib_icon  = "🛡️" if status == "지지" else "⚠️"
        fib_msg = "현재가가 이 라인 위에 있어 '지지선' 역할을 하고 있어요." if status == "지지" \
            else "현재가가 이 라인 아래로 내려가 '저항선'으로 바뀐 상태예요."
        st.markdown(f"""
        <div style="background:#0f172a; border:1px solid {fib_color}55; border-radius:8px;
            padding:10px 14px; margin:6px 0 10px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:12.5px; color:#e2e8f0; font-weight:700;">{fib_icon} 피보나치 되돌림 {pct*100:.1f}%</span>
            <span style="font-size:11.5px; color:{fib_color}; font-weight:700;">{status} ({gap_pct:+.1f}%)</span>
        </div>
        <div style="font-size:11px; color:#94a3b8; margin-top:4px;">
            기준가 <b style="color:#f1f5f9;">{price:,.0f}원</b> — 52주 고점·저점 사이에서 되돌림이 자주 나오는 가격대예요. {fib_msg}
        </div>
        </div>
        """, unsafe_allow_html=True)
        
    #변동성 경고 표시
    if volatility_warning:
        st.warning(volatility_warning)
        
def render_community_tab(naver_posts):
    st.markdown("#### 🔥 실시간 주주 비명소리")
    tab1, = st.tabs(["📌 네이버 인기글 (실시간 공감순)"])   
    with tab1:
        cols_post = st.columns(2)  # 2열 그리드로 가독성 향상
        for idx, post in enumerate(naver_posts[:8], 0):
            likes = post['likes']
            badge_color = "#16a34a" if likes >= 20 else "#ca8a04" if likes >= 5 else "#475569"
            with cols_post[idx % 2]:
                st.markdown(
                    f"""<div style="background:#0f172a; border-radius:8px; padding:9px 11px;
                        margin-bottom:8px; border-left:3px solid {badge_color};">
                    <div style="font-size:12px; color:#e2e8f0; line-height:1.4; margin-bottom:4px;">{post['title']}</div>
                    <div style="font-size:10.5px; color:#64748b;">👍 {post['likes']} &nbsp;·&nbsp; 👀 {post['views']}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

