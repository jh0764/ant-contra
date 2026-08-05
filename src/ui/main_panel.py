import streamlit as st
from constants import PRICE_COLOR, THEME, SPACING
from ui.common import html_block
import re


def render_price_info(
    current_price, change_pct, ant_refund_line, fib, volatility_warning
):
    is_up = change_pct >= 0
    p_color = PRICE_COLOR["up"] if is_up else PRICE_COLOR["down"]
    p_bg = "#fee2e2" if is_up else "#dbeafe"
    arrow = "▲" if is_up else "▼"

    # 개미 평단 대비 구간 강조 (뱃지 배경 제거 -> 텍스트 심볼 강조)
    is_loss = current_price < ant_refund_line
    vwap_status = "손실 구간" if is_loss else "수익 구간"
    vwap_color = (
        PRICE_COLOR["up"] if is_loss else PRICE_COLOR["down"]
    )  # 손실 시 경고성 붉은색 텍스트

    st.markdown(
        f"""
    <div style="margin-top:8px; margin-bottom:16px;">
      <!-- 메인 가격 영역 (1순위 강조: 뱃지 사용) -->
      <div style="display:flex; align-items:baseline; gap:10px;">
        <span style="font-size:34px; font-weight:900; color:{p_color}; letter-spacing:-0.5px;">{current_price:,}원</span>
        <span style="background:{p_bg}; color:{p_color}; font-weight:700; font-size:13.5px; padding:3px 10px; border-radius:6px;">{arrow} {change_pct:+.2f}%</span>
      </div>
      
      <!-- 개미 평단 추정선 (2순위 서브 강조: 점 구분 기호 + 컬러 텍스트) -->
      <div style="display:flex; align-items:center; gap:6px; margin-top:6px; font-size:12.5px;">
        <span style="color:{THEME['text_sub']}; font-weight:500;">개미 평단 추정선</span>
        <span style="color:{THEME['text_main']}; font-weight:700;">{ant_refund_line:,}원</span>
        <span style="color:{THEME['border']}; font-size:10px;">•</span>
        <span style="color:{vwap_color}; font-weight:800;">{vwap_status}</span>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if fib:
        pct, price, status = fib
        gap_pct = (current_price - price) / price * 100
        is_support = status == "지지"
        accent_color = PRICE_COLOR["up"] if is_support else PRICE_COLOR["down"]
        badge_bg = "#fee2e2" if is_support else "#dbeafe"

        # 핵심 키워드 강조 처리
        role_highlight = (
            f"<b style='color:{accent_color}; font-weight:700;'>지지선</b>"
            if is_support
            else f"<b style='color:{accent_color}; font-weight:700;'>저항선</b>"
        )
        fib_msg = (
            f"현재가가 이 라인 위에 있어 {role_highlight} 역할 수행 중"
            if is_support
            else f"현재가가 이 라인 아래에 있어 {role_highlight}으로 변환"
        )

        # 아래쪽 border-bottom 제거 (펀더멘털 영역 상단 선과 중복 방지)
        st.markdown(
            f"""
        <div style="padding:14px 0 10px 0; border-top:1px solid rgba(15,23,42,0.1); margin-top:14px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:4px;">
                <div>
                    <span style="font-size:11.5px; color:{THEME['text_sub']}; font-weight:700; letter-spacing:-0.2px;">피보나치 되돌림 <b style="color:{THEME['text_main']};">({pct*100:.1f}%)</b></span>
                    <div style="font-size:18px; font-weight:900; color:{THEME['text_main']}; margin-top:2px; letter-spacing:-0.3px;">{price:,.0f}원</div>
                </div>
                <div style="background:{badge_bg}; padding:4px 10px; border-radius:6px; margin-top:2px;">
                    <span style="font-size:12.5px; font-weight:800; color:{accent_color};">{status} {gap_pct:+.1f}%</span>
                </div>
            </div>
            <div style="font-size:11.5px; color:{THEME['text_sub']}; margin-top:2px;">
                {fib_msg}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_community_tab(naver_posts, ai_reason=None, ticker_code=None):
    clean_code = None

    # 1. 전달받은 ticker_code에서 숫자 6자리 추출 (예: '034020')
    if ticker_code:
        digits = re.findall(r"\d{1,6}", str(ticker_code))
        if digits:
            clean_code = digits[0].zfill(6)

    # 2. ticker_code 추출 실패 시 naver_posts 데이터 내부에서 탐색
    if not clean_code and naver_posts and isinstance(naver_posts, list):
        for post in naver_posts:
            if isinstance(post, dict):
                for key in ["code", "ticker", "symbol", "stock_code"]:
                    val = post.get(key)
                    if val:
                        digits = re.findall(r"\d{1,6}", str(val))
                        if digits:
                            clean_code = digits[0].zfill(6)
                            break
            if clean_code:
                break

    # 3. 네이버 종목토론방 URL 생성
    if clean_code:
        naver_board_url = (
            f"https://finance.naver.com/item/board.naver?code={clean_code}"
        )
    else:
        naver_board_url = "https://finance.naver.com/"
    # 상단 여백(margin-top:24px) 및 외부 링크 설정 (target="_blank")
    st.markdown(
        f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:24px; margin-bottom:6px;">
        <a href="{naver_board_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:inherit;">
            <span style="font-size:14px; font-weight:800; color:{THEME['text_main']};">실시간 주주 비명소리</span>
        </a>
        <a href="{naver_board_url}" target="_blank" rel="noopener noreferrer" title="네이버 종목토론방 바로가기" style="text-decoration:none; display:inline-flex; align-items:center;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
                 style="transition:stroke 0.2s; cursor:pointer;"
                 onmouseover="this.style.stroke='#111827'"
                 onmouseout="this.style.stroke='#9ca3af'">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
            </svg>
        </a>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if ai_reason:
        st.markdown(
            f"<p style='font-size:11.5px; color:{THEME['text_sub']}; margin-top:-2px; margin-bottom:10px;'>{ai_reason}</p>",
            unsafe_allow_html=True,
        )

    if not naver_posts:
        st.caption("수집된 게시글이 없습니다.")
        return

    # 게시글 별 링크 설정
    for post in naver_posts[:4]:
        likes = post.get("likes", 0)
        views = post.get("views", 0)
        max_likes = max((p.get("likes", 0) for p in naver_posts), default=1) or 1
        ratio = likes / max_likes
        badge_color = (
            "#16a34a"
            if ratio >= 0.7
            else "#ca8a04"
            if ratio >= 0.3
            else THEME["text_sub"]
        )
        post_url = post.get("url") or naver_board_url

        st.markdown(
            f"""<a href="{post_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:inherit; display:block;">
            <div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:6px; padding:7px 10px; box-shadow:0 4px 14px rgba(31,38,135,0.05);
                margin-bottom:6px; border-left:3px solid {badge_color}; display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:11.5px; color:{THEME['text_main']}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:70%;">
                {post['title']}
            </div>
            <div style="font-size:10px; color:{THEME['text_sub']}; white-space:nowrap;">
                👍 {likes} &nbsp;·&nbsp; 👀 {views}
            </div>
            </div></a>""",
            unsafe_allow_html=True,
        )

    # 게시글 더보기
    if len(naver_posts) > 4:
        more_count = len(naver_posts) - 4
        more_label = f"게시글 더보기 ({min(more_count,4)})"

        with st.expander(more_label, expanded=False):
            for post in naver_posts[4:8]:
                likes = post.get("likes", 0)
                views = post.get("views", 0)
                post_url = post.get("url") or naver_board_url
                st.markdown(
                    f"""<a href="{post_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; color:inherit; display:block;">
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid {THEME['border']};">
                    <span style="font-size:11.5px; color:{THEME['text_main']}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:70%;">{post['title']}</span>
                    <span style="font-size:10px; color:{THEME['text_sub']};">👍 {likes} · 👀 {views}</span>
                    </div></a>""",
                    unsafe_allow_html=True,
                )


def render_news_headlines(headlines):
    if not headlines:
        return
    st.markdown(
        f"<p style='font-size:13px; font-weight:700; color:{THEME['text_main']}; margin:4px 0 6px 0;'>📰 최근 뉴스</p>",
        unsafe_allow_html=True,
    )
    for h in headlines:
        st.markdown(
            f"""<a href="{h['link']}" target="_blank" style="text-decoration:none;">
            <div style="background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:8px; padding:8px 12px; margin-bottom:6px; box-shadow:0 4px 14px rgba(31,38,135,0.05);">
            <div style="font-size:12px; color:{THEME['text_main']}; font-weight:600; line-height:1.4;">{h['title']}</div>
            <div style="font-size:10px; color:{THEME['text_sub']}; margin-top:3px;">{h['press']} · {h['date']}</div>
            </div></a>""",
            unsafe_allow_html=True,
        )


def render_fundamental_stats(fundamentals):
    cap = fundamentals.get("market_cap", "N/A")
    per = fundamentals.get("per", "N/A")
    pbr = fundamentals.get("pbr", "N/A")
    eps = fundamentals.get("eps", "N/A")
    div = fundamentals.get("dividend_yield", "N/A")

    # 하단 border-bottom 제거 및 margin-bottom으로 탭과의 간격만 확보
    st.markdown(
        f"""
    <div style="border-top:1px solid rgba(15,23,42,0.1); padding-top:14px; margin-top:12px; margin-bottom:32px;">
        <div style="display:grid; grid-template-columns: 1.4fr 1fr 1fr 1.2fr 1fr; gap:4px; text-align:left;">
            <div>
                <div style="font-size:10.5px; color:{THEME['text_sub']}; font-weight:500;">시가총액</div>
                <div style="font-size:12.5px; color:{THEME['text_main']}; font-weight:700; white-space:nowrap; margin-top:2px;">{cap}</div>
            </div>
            <div style="border-left:1px solid rgba(15,23,42,0.12); padding-left:10px;">
                <div style="font-size:10.5px; color:{THEME['text_sub']}; font-weight:500;">PER</div>
                <div style="font-size:12.5px; color:{THEME['text_main']}; font-weight:700; margin-top:2px;">{per}</div>
            </div>
            <div style="border-left:1px solid rgba(15,23,42,0.12); padding-left:10px;">
                <div style="font-size:10.5px; color:{THEME['text_sub']}; font-weight:500;">PBR</div>
                <div style="font-size:12.5px; color:{THEME['text_main']}; font-weight:700; margin-top:2px;">{pbr}</div>
            </div>
            <div style="border-left:1px solid rgba(15,23,42,0.12); padding-left:10px;">
                <div style="font-size:10.5px; color:{THEME['text_sub']}; font-weight:500;">EPS</div>
                <div style="font-size:12.5px; color:{THEME['text_main']}; font-weight:700; white-space:nowrap; margin-top:2px;">{eps}</div>
            </div>
            <div style="border-left:1px solid rgba(15,23,42,0.12); padding-left:10px;">
                <div style="font-size:10.5px; color:{THEME['text_sub']}; font-weight:500;">배당수익률</div>
                <div style="font-size:12.5px; color:{THEME['text_main']}; font-weight:700; margin-top:2px;">{div}</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
