import streamlit as st

def html_block(content: str):
    lines = [line.lstrip() for line in content.strip("\n").splitlines()]
    st.markdown("\n".join(lines), unsafe_allow_html=True)