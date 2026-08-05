import streamlit as st
from constants import THEME


def render_landing():
    """랜딩 페이지 하단 경고 문구 (들여쓰기 제거로 코드 블록 오류 방지)"""
    st.markdown(
        f"""<div style="text-align: center; padding: 24px 0 12px 0;">
<span style="font-size: 11.5px; color: {THEME['text_sub']};">⚠️ 본 서비스는 투자 참고용이며, 투자 판단의 최종 책임은 본인에게 있습니다</span>
</div>""",
        unsafe_allow_html=True,
    )
