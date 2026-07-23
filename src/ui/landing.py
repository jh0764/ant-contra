import streamlit as st
from constants import THEME


def render_landing():
    st.markdown(f"""
    <div style="text-align:center; padding: 0 20px 2px 20px;">
      <span style="font-size:11.5px; color:{THEME['text_sub']};">
        ⚠️ 본 서비스는 투자 참고용이며, 투자 판단의 최종 책임은 본인에게 있습니다
      </span>
    </div>
    """, unsafe_allow_html=True)