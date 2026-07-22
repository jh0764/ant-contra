import streamlit as st
from constants import THEME

def html_block(content: str):
    lines = [line.lstrip() for line in content.strip("\n").splitlines()]
    st.markdown("\n".join(lines), unsafe_allow_html=True)

def render_tab_group(options, key, default_index=0, size="md", selected_color=None,
                      margin_bottom="0px"):
    scope = f"{key}_scope"
    selected_color = selected_color or THEME['text_main']
    if size == "sm":
        pad, font_size, radius, group_radius = "2px 8px", "9px", "5px", "7px"
    else:
        pad, font_size, radius, group_radius = "4px 14px", "12px", "7px", "9px"
        
    st.markdown(f"""
    <style>
    div.st-key-{scope} {{
        margin-bottom:{margin_bottom} !important;
    }}
    div.st-key-{scope} [data-testid="stElementContainer"] {{
        margin-bottom:0 !important;
    }}
    div.st-key-{scope} [data-testid="stWidgetLabel"] {{
        display:none !important;
    }}
    div.st-key-{scope} [data-testid="stButtonGroup"] {{
        width:fit-content !important;
    }}
    div.st-key-{scope} div[data-baseweb="button-group"] {{
        background:{THEME['border']}66 !important;
        border-radius:{group_radius} !important;
        padding:2px !important;
        gap:2px !important;
        display:inline-flex !important;
    }}
    div.st-key-{scope} div[data-baseweb="button-group"] button[data-testid="stBaseButton-pills"],
    div.st-key-{scope} div[data-baseweb="button-group"] button[data-testid="stBaseButton-pillsActive"] {{
        padding:{pad} !important;
        height:auto !important;
        min-height:0 !important;
        max-height:none !important;
        border:none !important;
        border-radius:{radius} !important;
        background:transparent !important;
        box-shadow:none !important;
        display:flex !important;
        align-items:center !important;
        justify-content:center !important;
    }}
    div.st-key-{scope} button [data-testid="stMarkdownContainer"] {{
        display:flex !important;
        align-items:center !important;
        padding:0 !important;
        margin:0 !important;
        line-height:1 !important;
    }}
    div.st-key-{scope} button[data-testid="stBaseButton-pills"] p {{
        font-size:{font_size} !important;
        font-weight:600 !important;
        color:{THEME['text_sub']} !important;
        margin:0 !important;
        padding:0 !important;
        line-height:1 !important;
        white-space:nowrap !important;
    }}
    div.st-key-{scope} button[data-testid="stBaseButton-pillsActive"] {{
        background:{THEME['surface']} !important;
        box-shadow:0 1px 3px rgba(0,0,0,0.12) !important;
    }}
    div.st-key-{scope} button[data-testid="stBaseButton-pillsActive"] p {{
        font-size:{font_size} !important;
        font-weight:700 !important;
        color:{selected_color} !important;
        margin:0 !important;
        padding:0 !important;
        line-height:1 !important;
        white-space:nowrap !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    with st.container(key=scope):
        result = st.pills(
            label="", options=options, default=options[default_index],
            selection_mode="single", label_visibility="collapsed", key=key
        )
    return result if result else options[default_index]

def render_flex_row(row_key, gap="12px", margin_bottom="8px"):
    st.markdown(f"""
    <style>
    div.st-key-{row_key} > div[data-testid="stVerticalBlock"] {{
        display:flex !important;
        flex-direction:row !important;
        flex-wrap:nowrap !important;
        align-items:center !important;
        justify-content:space-between !important;
        gap:{gap} !important;
    }}
    div.st-key-{row_key} div[data-testid="stElementContainer"] {{
        width:auto !important;
        flex:0 0 auto !important;
        margin:0 !important;
    }}
    div.st-key-{row_key} {{
        margin-bottom:{margin_bottom} !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    return st.container(key=row_key)