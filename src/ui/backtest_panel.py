import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
import os
import time
from core.backtest import (
    run_universe_backtest,
    summarize_backtest,
    get_baseline_returns,
    FORWARD_WINDOWS,
)

MIN_RELIABLE_N = 20

COLOR_PERIOD_5 = "#93C5FD"  # 5일
COLOR_PERIOD_10 = "#3B82F6"  # 10일
COLOR_PERIOD_20 = "#1E40AF"  # 20일

COLOR_WIN = "#3B82F6"  # 승률 (메인 블루)
COLOR_LOSS = "#BAE6FD"  # 패율 (소프트 연청)

COLOR_BG_CARD = "#FFFFFF"
COLOR_TEXT_MAIN = "#0F172A"
COLOR_TEXT_SUB = "#64748B"
COLOR_BORDER = "#E2E8F0"
COLOR_HOVER_BG = "#F8FAFC"

DINO_LOADER_HTML = """
<style>
.dino-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
}
.dino-svg {
    width: 96px;
    height: 96px;
}
@keyframes leg-frame-1-anim {
    0%, 32%, 100% { opacity: 1; }
    33%, 99% { opacity: 0; }
}
@keyframes leg-frame-2-anim {
    33%, 65% { opacity: 1; }
    0%, 32%, 66%, 100% { opacity: 0; }
}
@keyframes leg-frame-3-anim {
    66%, 99% { opacity: 1; }
    0%, 65%, 100% { opacity: 0; }
}
.leg-1 { animation: leg-frame-1-anim 0.3s infinite; }
.leg-2 { animation: leg-frame-2-anim 0.3s infinite; }
.leg-3 { animation: leg-frame-3-anim 0.3s infinite; }
.loader-text {
    margin-top: 8px;
    font-size: 13px;
    color: #64748B;
    font-weight: 600;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    text-align: center;
}
</style>

<div class="dino-container">
    <svg class="dino-svg" viewBox="0 0 24 24" shape-rendering="crispEdges">
        <!-- 공룡 몸통, 꼬리, 팔, 눈, 입 (X: 0~23, Y: 0~19) -->
        <path fill="#535353" d="
            M13,0 h10 v1 h-10 z
            M12,1 h12 v1 h-12 z
            M12,2 h2 v2 h-2 z M16,2 h8 v2 h-8 z
            M12,4 h12 v2 h-12 z
            M12,6 h6 v2 h-6 z
            M12,8 h10 v1 h-10 z
            M0,9 h1 v1 h-1 z M10,9 h7 v1 h-7 z
            M0,10 h1 v1 h-1 z M8,10 h9 v1 h-9 z
            M0,11 h2 v1 h-2 z M7,11 h12 v1 h-12 z
            M0,12 h3 v1 h-3 z M6,12 h11 v1 h-11 z M18,12 h1 v1 h-1 z
            M0,13 h17 v1 h-17 z
            M0,14 h17 v1 h-17 z
            M1,15 h16 v1 h-16 z
            M2,16 h14 v1 h-14 z
            M3,17 h12 v1 h-12 z
            M4,18 h10 v1 h-10 z
            M5,19 h8 v1 h-8 z
        " />

        <!-- 다리 애니메이션 프레임 1 (0% / 100%) -->
        <g class="leg-1">
            <path fill="#535353" d="
                M6,20 h3 v1 h-3 z
                M6,21 h2 v1 h-2 z
                M6,22 h1 v1 h-1 z
                M6,23 h2 v1 h-2 z
                M11,20 h2 v1 h-2 z
                M12,21 h1 v2 h-1 z
                M12,23 h2 v1 h-2 z
            " />
        </g>

        <!-- 다리 애니메이션 프레임 2 (33%) -->
        <g class="leg-2">
            <path fill="#535353" d="
                M6,20 h3 v1 h-3 z
                M6,21 h2 v1 h-2 z
                M6,22 h1 v1 h-1 z
                M6,23 h2 v1 h-2 z
                M11,20 h3 v1 h-3 z
            " />
        </g>

        <!-- 다리 애니메이션 프레임 3 (66%) -->
        <g class="leg-3">
            <path fill="#535353" d="
                M6,20 h3 v1 h-3 z
                M7,21 h3 v1 h-3 z
                M11,20 h2 v1 h-2 z
                M12,21 h1 v2 h-1 z
                M12,23 h2 v1 h-2 z
            " />
        </g>
    </svg>
    <div class="loader-text">백테스트 모델 결과 계산 중...</div>
</div>
"""


def render_backtest_page():
    # 1. CSS 스타일 정의 (위치 이동 방지 및 모바일 가로 50:50 고정 배치)
    st.markdown(
        f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <style>
    .stApp {{ 
        background-color: #F8FAFC !important; 
    }}
    
    /* [버튼 컨테이너] 가로 정렬 및 간격 고정 */
    div[data-testid="stHorizontalBlock"]:has(button) {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 10px !important;
        margin-bottom: 12px !important;
    }}

    /* [버튼 컬럼] 최소 너비를 145px로 고정하여 창이 줄어들어도 컬럼끼리 겹치지 않음 */
    div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"] {{
        min-width: 145px !important;
        flex: 0 0 auto !important;
        padding: 0 !important;
    }}

    /* [버튼 스타일] 높이, 테두리, 폰트, 반응형 크기 완전 통일 */
    div[data-testid="stHorizontalBlock"]:has(button) button {{
        width: 100% !important;
        height: 38px !important;
        background-color: #ffffff !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 8px !important;
        color: #334155 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 0 14px !important;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.08) !important;
        transition: all 0.15s ease-in-out !important;
        white-space: nowrap !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
    }}

    div[data-testid="stHorizontalBlock"]:has(button) button:hover {{
        background-color: #ffffff !important;
        border-color: #cbd5e1 !important;
        color: #0f172a !important;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.08) !important;
        transform: translateY(-1px);
    }}

    div[data-testid="stHorizontalBlock"]:has(button) button p {{
        white-space: nowrap !important;
        font-size: 13px !important;
        line-height: 1 !important;
        margin: 0 !important;
    }}

    /* 버튼 아이콘 매핑 */
    div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"]:nth-child(1) button::before {{
        font-family: "Font Awesome 6 Free";
        content: "\\f015";
        font-weight: 900;
        margin-right: 7px;
        color: #64748b;
        font-size: 13px;
    }}

    div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"]:nth-child(2) button::before {{
        font-family: "Font Awesome 6 Free";
        content: "\\f021";
        font-weight: 900;
        margin-right: 7px;
        color: #64748b;
        font-size: 13px;
    }}

    /* [모바일 반응형 최적화] 화면 폭이 640px 이하일 때 처리 */
    @media (max-width: 640px) {{
        div[data-testid="stHorizontalBlock"]:has(button) {{
            flex-direction: row !important; /* 모바일에서도 세로 스택을 차단하고 가로 배치 유지 */
            gap: 8px !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(button) > div[data-testid="stColumn"] {{
            min-width: 0 !important;
            flex: 1 1 0px !important; /* 두 버튼을 모바일 화면 폭에 맞춰 정확히 50:50 균등 분할 */
        }}
        div[data-testid="stHorizontalBlock"]:has(button) button p {{
            font-size: 0px !important; /* 모바일에서는 깔끔하게 아이콘만 노출 */
        }}
        div[data-testid="stHorizontalBlock"]:has(button) button::before {{
            margin-right: 0px !important;
            font-size: 15px !important;
        }}
    }}

    /* 카드 상자 스타일 */
    .custom-card {{
        background-color: #FFFFFF;
        border: 1px solid {COLOR_BORDER};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }}

    .card-title {{
        font-size: 17px;
        font-weight: 700;
        color: {COLOR_TEXT_MAIN};
        letter-spacing: -0.3px;
        margin-bottom: 4px;
    }}

    .card-sub {{
        font-size: 12px;
        color: {COLOR_TEXT_SUB};
        margin-bottom: 16px;
    }}

    /* 내부 메트릭 그리드 */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 12px;
    }}

    .metric-item {{
        background-color: {COLOR_HOVER_BG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }}

    .metric-label {{ font-size: 12px; font-weight: 600; color: {COLOR_TEXT_SUB}; margin-bottom: 4px; }}
    .metric-val {{ font-size: 16px; font-weight: 800; color: {COLOR_PERIOD_10}; }}

    /* 드롭다운 스타일 */
    div[data-testid="stSelectbox"] {{
        transform: scale(0.85) !important;
        transform-origin: right center !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        border-radius: 6px !important;
    }}

    div[data-testid="stSelectbox"] input {{
        caret-color: transparent !important;
        pointer-events: none !important;
    }}

    div[data-baseweb="popover"] {{
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1) !important;
        border-radius: 6px !important;
    }}

    div[data-baseweb="popover"] li, 
    div[data-baseweb="popover"] div[role="option"] {{
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        min-height: 28px !important;
        padding-top: 4px !important;
        padding-bottom: 4px !important;
    }}

    /* 테이블 스타일 */
    .table-wrapper {{ width: 100%; overflow-x: auto; margin-top: 12px; }}
    .table-container {{ width: 100%; border-collapse: collapse; min-width: 600px; }}
    .table-container th {{ padding: 10px; color: {COLOR_TEXT_SUB}; font-size: 12px; font-weight: 700; text-align: center; border-bottom: 2px solid {COLOR_BORDER}; }}
    .table-container td {{ padding: 12px 10px; text-align: center; font-size: 13px; border-bottom: 1px solid {COLOR_BORDER}; }}
    .badge-sample {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 700; background-color: #F1F5F9; color: #475569; }}
    </style>
    """,
        unsafe_allow_html=True,
    )

    # 2. 버튼 영역 (상단 고정 배치)
    c1, c2, _ = st.columns([1.3, 1.3, 4.4], gap="medium")

    with c1:
        if st.button("메인으로 돌아가기", use_container_width=True):
            st.query_params.clear()
            st.rerun()
    with c2:
        if st.button("데이터 새로고침", use_container_width=True):
            run_universe_backtest.clear()
            st.rerun()

    # 3. 로딩 처리 영역
    loader_placeholder = st.empty()
    with loader_placeholder.container():
        st.info(
            "과거 3년치 데이터를 실시간으로 검증하므로, **최초 로딩 시 약 1~2분 정도의 시간이 소요**될 수 있습니다. 잠시만 기다려 주세요."
        )
        components.html(DINO_LOADER_HTML, height=130)

    # 4. 백테스트 연산
    bt_df = run_universe_backtest()

    # 5. 로딩 완료 후 정리
    loader_placeholder.empty()

    if bt_df.empty:
        st.warning("백테스트 결과를 계산하지 못했습니다.")
        return

    summary = summarize_backtest(bt_df)
    baseline = get_baseline_returns(bt_df)

    st.write("")

    # 카드 1: 종합 리포트
    st.html(
        f"""
    <div class="custom-card">
        <div class="card-title">점수 유효성 백테스트 종합 리포트</div>
        <div class="card-sub">과거 3년 유니버스 기준 (RSI·볼린저·낙폭·200일선·거래량·외국인·OBV 지표 검증)</div>
        <div class="metric-grid">
            <div class="metric-item">
                <div class="metric-label">전체 검증 표본</div>
                <div class="metric-val" style="color: {COLOR_TEXT_MAIN};">{len(bt_df):,} 건</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">5일 시장 평균</div>
                <div class="metric-val">{baseline[5]:+.2f}%</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">10일 시장 평균</div>
                <div class="metric-val">{baseline[10]:+.2f}%</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">20일 시장 평균</div>
                <div class="metric-val">{baseline[20]:+.2f}%</div>
            </div>
        </div>
    </div>
    """
    )

    # 카드 2: 차트 분석
    chart_container = st.container()
    with chart_container:
        st.markdown(
            '<div class="card-title">보유 기간별 예상 수익률 및 승률 분석</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="card-sub">점수대별 수익률 변화와 익절/손절 비율 분석 데이터입니다.</div>',
            unsafe_allow_html=True,
        )

        _render_grouped_return_chart(summary)
        st.divider()
        _render_win_rate_stacked_chart(summary)

    # 카드 3: 상세 통계 표
    _render_custom_table(summary)


def _render_grouped_return_chart(summary):
    categories = summary["점수구간"].tolist()

    r5 = summary.get("5일 평균수익률(%)", [0] * len(categories)).tolist()
    r10 = summary.get("10일 평균수익률(%)", [0] * len(categories)).tolist()
    r20 = summary.get("20일 평균수익률(%)", [0] * len(categories)).tolist()

    fig = go.Figure(
        data=[
            go.Bar(
                name="5일 보유",
                x=categories,
                y=r5,
                marker=dict(color=COLOR_PERIOD_5, cornerradius=4),
                text=[f"{v:+.2f}%" for v in r5],
                textposition="outside",
                textfont=dict(size=11, color=COLOR_PERIOD_5),
            ),
            go.Bar(
                name="10일 보유",
                x=categories,
                y=r10,
                marker=dict(color=COLOR_PERIOD_10, cornerradius=4),
                text=[f"{v:+.2f}%" for v in r10],
                textposition="outside",
                textfont=dict(size=11, color=COLOR_PERIOD_10),
            ),
            go.Bar(
                name="20일 보유",
                x=categories,
                y=r20,
                marker=dict(color=COLOR_PERIOD_20, cornerradius=4),
                text=[f"{v:+.2f}%" for v in r20],
                textposition="outside",
                textfont=dict(size=11, color=COLOR_PERIOD_20),
            ),
        ]
    )

    all_vals = r5 + r10 + r20
    max_y = max(all_vals) * 1.35 if all_vals else 5
    min_y = min(all_vals + [0]) * 1.1

    fig.update_layout(
        title=dict(
            text="• 보유 기간별 점수대 평균 수익률 비교",
            font=dict(size=13, color=COLOR_TEXT_MAIN),
            x=0,
        ),
        barmode="group",
        bargap=0.3,
        bargroupgap=0.08,
        height=320,
        margin=dict(l=0, r=0, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="right",
            x=1,
            font=dict(size=11, color=COLOR_TEXT_SUB),
        ),
        xaxis=dict(
            tickfont=dict(size=12, color=COLOR_TEXT_MAIN, weight="bold"), showgrid=False
        ),
        yaxis=dict(
            range=[min_y, max_y],
            showgrid=True,
            gridcolor="#F1F5F9",
            ticksuffix="%",
            tickfont=dict(size=11, color=COLOR_TEXT_SUB),
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _render_win_rate_stacked_chart(summary):
    # 컬럼 비율을 [2.5, 1.2]로 확보하여 텍스트 잘림 방지
    col_title, col_select = st.columns([2.5, 1.2])

    with col_title:
        st.markdown(
            '<div style="font-size:13px; font-weight:700; color:#0F172A; padding-top:4px;">• 점수대별 손익 승률 비율</div>',
            unsafe_allow_html=True,
        )
    with col_select:
        period_option = st.selectbox(
            "보유기간 선택",
            options=[5, 10, 20],
            format_func=lambda x: f"{x}일 보유 기준",
            index=1,
            key="win_rate_period_select",
            label_visibility="collapsed",
        )

    col_name = f"{period_option}일 승률(%)"
    categories = summary["점수구간"].tolist()
    win_rates = summary.get(col_name, [0] * len(categories)).tolist()
    loss_rates = [max(0, 100 - w) for w in win_rates]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=categories,
            x=win_rates,
            name="익절(승)",
            orientation="h",
            marker=dict(color=COLOR_WIN, cornerradius=4, line=dict(width=0)),
            text=[f"{v:.1f}%" for v in win_rates],
            textposition="inside",
            textfont=dict(color="#FFFFFF", size=11, weight="bold"),
        )
    )

    fig.add_trace(
        go.Bar(
            y=categories,
            x=loss_rates,
            name="손절(패)",
            orientation="h",
            marker=dict(color=COLOR_LOSS, cornerradius=4, line=dict(width=0)),
            text=[f"{v:.1f}%" for v in loss_rates],
            textposition="inside",
            textfont=dict(color="#0F172A", size=11, weight="bold"),
        )
    )

    fig.update_layout(
        barmode="stack",
        bargap=0.32,
        height=240,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, range=[0, 100], ticksuffix="%"),
        yaxis=dict(tickfont=dict(size=12, color=COLOR_TEXT_MAIN, weight="bold")),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="right",
            x=1,
            font=dict(size=11, color=COLOR_TEXT_SUB),
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _render_custom_table(summary):
    rows_html = ""
    for _, row in summary.iterrows():
        sample_cnt = row["표본수"]
        if sample_cnt >= MIN_RELIABLE_N:
            badge = f'<span class="badge-sample">{sample_cnt:,}건</span>'
        else:
            badge = f'<span class="badge-sample" style="background:#FEE2E2; color:#991B1B;">{sample_cnt:,}건 (미달)</span>'

        r5 = row.get("5일 평균수익률(%)", 0)
        r10 = row.get("10일 평균수익률(%)", 0)
        r20 = row.get("20일 평균수익률(%)", 0)

        rows_html += f"""
        <tr>
            <td style="font-weight:700; color:{COLOR_TEXT_MAIN};">{row['점수구간']}</td>
            <td>{badge}</td>
            <td style="font-weight:700; color:{COLOR_PERIOD_10};">{r5:+.2f}%</td>
            <td style="font-weight:600; color:{COLOR_TEXT_MAIN};">{row.get('5일 승률(%)', 0):.1f}%</td>
            <td style="font-weight:700; color:{COLOR_PERIOD_10};">{r10:+.2f}%</td>
            <td style="font-weight:600; color:{COLOR_TEXT_MAIN};">{row.get('10일 승률(%)', 0):.1f}%</td>
            <td style="font-weight:700; color:{COLOR_PERIOD_10};">{r20:+.2f}%</td>
        </tr>
        """

    st.html(
        f"""
    <div class="custom-card">
        <div class="card-title">상세 통계 데이터 리포트</div>
        <div class="card-sub">각 점수 구간별 백테스트 상세 수치 데이터입니다.</div>
        <div class="table-wrapper">
            <table class="table-container">
                <thead>
                    <tr>
                        <th>점수 구간</th>
                        <th>표본 수</th>
                        <th>5일 평균수익률</th>
                        <th>5일 승률</th>
                        <th>10일 평균수익률</th>
                        <th>10일 승률</th>
                        <th>20일 평균수익률</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        <div style="font-size:11.5px; color:{COLOR_TEXT_SUB}; margin-top:12px; line-height:1.4;">
            • 표본수가 20건 미만인 구간은 통계적 신뢰도가 낮아 의사결정에 주의가 필요합니다.
        </div>
    </div>
    """
    )
