import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from constants import THEME
from core.backtest import run_universe_backtest, summarize_backtest, get_baseline_returns, FORWARD_WINDOWS

MIN_RELIABLE_N = 20

BUCKET_COLORS = ["#16a34a", "#475569", "#ca8a04", "#ea580c", "#dc2626"]


def render_backtest_page():
    st.markdown(f"<div style='font-size:22px; font-weight:800; color:{THEME['text_main']}; margin-bottom:4px;'>📊 점수 유효성 백테스트</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:12px; color:{THEME['text_sub']}; margin-bottom:14px;'>"
        f"객관지표 점수(RSI·볼린저·낙폭·200일선·거래량·외국인·OBV)만 검증 대상입니다. "
        f"커뮤니티 감성점수는 과거 데이터가 없어 제외됩니다. 최근 3년, 스캔 유니버스(코스피+코스닥) 기준.</div>",
        unsafe_allow_html=True
    )

    col_back, col_refresh = st.columns([1, 1])
    with col_back:
        if st.button("⬅ 메인으로"):
            st.query_params.clear()
            st.rerun()
    with col_refresh:
        if st.button("🔄 새로고침 (캐시 무시하고 재계산)"):
            run_universe_backtest.clear()
            st.rerun()

    with st.spinner("과거 3년 데이터로 점수 재계산 중... (최초 실행 시 1~2분 소요, 이후 캐시)"):
        bt_df = run_universe_backtest()

    if bt_df.empty:
        st.warning("백테스트 결과를 계산하지 못했습니다.")
        return

    st.caption(f"⏱ 이 결과는 실시간이 아니라 최대 6시간 캐시됩니다 · 계산 시각: {datetime.now().strftime('%Y-%m-%d %H:%M')} 기준 (새로고침 전까지 고정)")

    summary = summarize_backtest(bt_df)
    baseline = get_baseline_returns(bt_df)

    st.markdown(
        f"<div style='background:{THEME['surface']}; border:1px solid {THEME['border']}; border-radius:10px; "
        f"padding:10px 14px; margin:10px 0 8px 0; font-size:12.5px; color:{THEME['text_sub']};'>"
        f"<b style='color:{THEME['text_main']};'>기준선</b> — 점수와 무관하게 유니버스를 그냥 들고 있었을 때 평균 수익률: "
        f"5일 <b>{baseline[5]:+.2f}%</b> · 10일 <b>{baseline[10]:+.2f}%</b> · 20일 <b>{baseline[20]:+.2f}%</b><br>"
        f"막대가 이 점선보다 위에 있어야 \"점수가 실제로 도움이 된다\"는 뜻입니다."
        f"</div>",
        unsafe_allow_html=True
    )

    for w in FORWARD_WINDOWS:
        _render_horizon_chart(summary, w, baseline[w])

    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.caption(f"전체 표본 수: {len(bt_df)}건 · 표본수 {MIN_RELIABLE_N}건 미만 구간(색이 흐린 막대)은 통계적으로 신뢰하기 어렵습니다.")


def _render_horizon_chart(summary, window, baseline_val):
    col = f"{window}일 평균수익률(%)"
    if col not in summary.columns or summary.empty:
        return

    y_vals = [v if pd.notna(v) else 0 for v in summary[col]]
    opacities = [
        1.0 if (n >= MIN_RELIABLE_N) else (0.25 if n == 0 else 0.45)
        for n in summary["표본수"]
    ]
    text_labels = [
        "표본없음" if n == 0 else (f"n={n}" if n >= MIN_RELIABLE_N else f"n={n} ⚠️")
        for n in summary["표본수"]
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=summary["점수구간"], y=y_vals,
        marker=dict(color=BUCKET_COLORS[:len(summary)], opacity=opacities),
        text=text_labels,
        textposition="outside",
        hovertemplate="%{x}<br>평균수익률 %{y:.2f}%<extra></extra>",
    ))
    fig.add_hline(y=baseline_val, line_dash="dot", line_color=THEME['text_sub'])

    fig.update_layout(
        title=dict(text=f"{window}일 뒤 평균 수익률 (점선=기준선)", font=dict(size=13, color=THEME['text_main'])),
        height=260, margin=dict(l=10, r=10, t=36, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(tickfont=dict(size=11)),
        yaxis=dict(gridcolor=THEME['border'], ticksuffix="%", tickfont=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
