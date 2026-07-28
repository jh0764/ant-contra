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
        st.markdown(
            f"<div style='font-size:11px; color:{THEME['text_sub']}; background:#FEF3C7; "
            f"border:1px solid #FDE68A; border-radius:6px; padding:6px 10px; margin-top:6px;'>"
            f"⚠️ {volatility_warning}</div>",
            unsafe_allow_html=True
        )

def render_community_tab(naver_posts, ai_reason=None, ticker_code=None):
# 네이버 종목토론방 바로가기 URL 생성
    naver_board_url = f"https://finance.naver.com/item/board.naver?code={ticker_code}" if ticker_code else "#"

# 이미지와 동일한 링크(Link) 모양의 SVG 아이콘 배치
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
        <span style="font-size:14px; font-weight:800; color:{THEME['text_main']};">실시간 주주 비명소리</span>
        <a href="{naver_board_url}" target="_blank" title="네이버 종목토론방 바로가기" style="text-decoration:none; display:inline-flex; align-items:center;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
                 style="transition:stroke 0.2s; cursor:pointer;"
                 onmouseover="this.style.stroke='#111827'"
                 onmouseout="this.style.stroke='#9ca3af'">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
            </svg>
        </a>
    </div>
    """, unsafe_allow_html=True)
    if ai_reason:
        st.markdown(
            f"<p style='font-size:11.5px; color:{THEME['text_sub']}; margin-top:-2px; margin-bottom:10px;'>{ai_reason}</p>",
            unsafe_allow_html=True
        )

    if not naver_posts:
        st.caption("수집된 게시글이 없습니다.")
        return

    # 상위 4개만 한 줄 형태 컴팩트 카드로 렌더링
    for post in naver_posts[:4]:
        likes = post.get('likes', 0)
        views = post.get('views', 0)
        badge_color = "#16a34a" if likes >= 20 else "#ca8a04" if likes >= 5 else THEME['text_sub']
        
        st.markdown(
            f"""<div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:6px; padding:7px 10px;
                margin-bottom:6px; border-left:3px solid {badge_color}; display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:11.5px; color:{THEME['text_main']}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:70%;">
                {post['title']}
            </div>
            <div style="font-size:10px; color:{THEME['text_sub']}; white-space:nowrap;">
                👍 {likes} &nbsp;·&nbsp; 👀 {views}
            </div>
            </div>""",
            unsafe_allow_html=True
        )

# 게시글 더보기
    if len(naver_posts) > 4:
        more_count = len(naver_posts) - 4
        # 이모티콘 제거
        more_label = f"게시글 더보기 ({more_count})"
        
        with st.expander(more_label, expanded=False):
            for post in naver_posts[4:8]:
                likes = post.get('likes', 0)
                views = post.get('views', 0)
                st.markdown(
                    f"""<div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid {THEME['border']};">
                    <span style="font-size:11.5px; color:{THEME['text_main']}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:70%;">{post['title']}</span>
                    <span style="font-size:10px; color:{THEME['text_sub']};">👍 {likes} · 👀 {views}</span>
                    </div>""",
                    unsafe_allow_html=True
                )

def render_news_headlines(headlines):
    if not headlines:
        return
    st.markdown(f"<p style='font-size:13px; font-weight:700; color:{THEME['text_main']}; margin:4px 0 6px 0;'>📰 최근 뉴스</p>", unsafe_allow_html=True)
    for h in headlines:
        st.markdown(
            f"""<a href="{h['link']}" target="_blank" style="text-decoration:none;">
            <div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:8px; padding:8px 12px; margin-bottom:6px;">
            <div style="font-size:12px; color:{THEME['text_main']}; font-weight:600; line-height:1.4;">{h['title']}</div>
            <div style="font-size:10px; color:{THEME['text_sub']}; margin-top:3px;">{h['press']} · {h['date']}</div>
            </div></a>""",
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