import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.backtest import run_universe_backtest, summarize_backtest, get_baseline_returns, FORWARD_WINDOWS

MIN_RELIABLE_N = 20

COLOR_PERIOD_5 = "#93C5FD"    # 5일
COLOR_PERIOD_10 = "#3B82F6"   # 10일
COLOR_PERIOD_20 = "#1E40AF"   # 20일

COLOR_WIN = "#3B82F6"         # 승률 (메인 블루)
COLOR_LOSS = "#BAE6FD"        # 패율 (소프트 연청)

COLOR_BG_CARD = "#FFFFFF"
COLOR_TEXT_MAIN = "#0F172A"
COLOR_TEXT_SUB = "#64748B"
COLOR_BORDER = "#E2E8F0"
COLOR_HOVER_BG = "#F8FAFC"


def render_backtest_page():
    # 1. CSS 스타일 정의
    st.markdown(f"""
    <style>
    .stApp {{ 
        background-color: #F8FAFC !important; 
    }}
    
    /* 상단 버튼 스타일 */
    .stButton > button {{
        width: 100% !important;
        background-color: #FFFFFF !important;
        color: {COLOR_TEXT_MAIN} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
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

/* 1. 드롭다운 본체: 크기 축소 및 그림자 추가 */
    div[data-testid="stSelectbox"] {{
        transform: scale(0.85) !important;
        transform-origin: right center !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        border-radius: 6px !important;
    }}

    /* 입력 커서 및 선택 취소 동작 방지 */
    div[data-testid="stSelectbox"] input {{
        caret-color: transparent !important;
        pointer-events: none !important;
    }}

    /* 2. 내부 아코디언 팝업 메뉴: scale 변환 제거 후 폰트/크기만 본체에 맞춤 */
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
    """, unsafe_allow_html=True)

    # 2. 상단 버튼
    c1, c2 = st.columns(2)
    with c1:
        if st.button("메인으로 돌아가기"):
            st.query_params.clear()
            st.rerun()
    with c2:
        if st.button("데이터 새로고침"):
            run_universe_backtest.clear()
            st.rerun()

    with st.spinner("백테스트 모델 결과 로딩 중..."):
        bt_df = run_universe_backtest()

    if bt_df.empty:
        st.warning("백테스트 결과를 계산하지 못했습니다.")
        return

    summary = summarize_backtest(bt_df)
    baseline = get_baseline_returns(bt_df)

    st.write("")

    # 카드 1: 종합 리포트
    st.html(f"""
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
    """)

    # 카드 2: 차트 분석 (위쪽 빈 상자 문제 원인 제거)
    chart_container = st.container()
    with chart_container:
        st.markdown('<div class="card-title">보유 기간별 예상 수익률 및 승률 분석</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-sub">점수대별 수익률 변화와 익절/손절 비율 분석 데이터입니다.</div>', unsafe_allow_html=True)
        
        # 차트 1
        _render_grouped_return_chart(summary)
        
        st.divider()
        
        # 차트 2
        _render_win_rate_stacked_chart(summary)

    # 카드 3: 상세 통계 표
    _render_custom_table(summary)


def _render_grouped_return_chart(summary):
    categories = summary["점수구간"].tolist()

    r5 = summary.get('5일 평균수익률(%)', [0]*len(categories)).tolist()
    r10 = summary.get('10일 평균수익률(%)', [0]*len(categories)).tolist()
    r20 = summary.get('20일 평균수익률(%)', [0]*len(categories)).tolist()

    fig = go.Figure(data=[
        go.Bar(
            name='5일 보유', x=categories, y=r5, 
            marker=dict(color=COLOR_PERIOD_5, cornerradius=4), 
            text=[f"{v:+.2f}%" for v in r5], 
            textposition='outside',
            textfont=dict(size=11, color=COLOR_PERIOD_5)
        ),
        go.Bar(
            name='10일 보유', x=categories, y=r10, 
            marker=dict(color=COLOR_PERIOD_10, cornerradius=4), 
            text=[f"{v:+.2f}%" for v in r10], 
            textposition='outside',
            textfont=dict(size=11, color=COLOR_PERIOD_10)
        ),
        go.Bar(
            name='20일 보유', x=categories, y=r20, 
            marker=dict(color=COLOR_PERIOD_20, cornerradius=4), 
            text=[f"{v:+.2f}%" for v in r20], 
            textposition='outside',
            textfont=dict(size=11, color=COLOR_PERIOD_20)
        )
    ])

    all_vals = r5 + r10 + r20
    max_y = max(all_vals) * 1.35 if all_vals else 5
    min_y = min(all_vals + [0]) * 1.1

    fig.update_layout(
        title=dict(text="• 보유 기간별 점수대 평균 수익률 비교", font=dict(size=13, color=COLOR_TEXT_MAIN), x=0),
        barmode='group',
        bargap=0.3,
        bargroupgap=0.08,
        height=320,
        margin=dict(l=0, r=0, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h", 
            yanchor="bottom", y=1.05, 
            xanchor="right", x=1,
            font=dict(size=11, color=COLOR_TEXT_SUB)
        ),
        xaxis=dict(tickfont=dict(size=12, color=COLOR_TEXT_MAIN, weight="bold"), showgrid=False),
        yaxis=dict(
            range=[min_y, max_y], 
            showgrid=True, 
            gridcolor="#F1F5F9", 
            ticksuffix="%", 
            tickfont=dict(size=11, color=COLOR_TEXT_SUB)
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def _render_win_rate_stacked_chart(summary):
    # 컬럼 비율을 [2.5, 1.2]로 확보하여 텍스트 잘림 방지
    col_title, col_select = st.columns([2.5, 1.2])
    
    with col_title:
        st.markdown('<div style="font-size:13px; font-weight:700; color:#0F172A; padding-top:4px;">• 점수대별 손익 승률 비율</div>', unsafe_allow_html=True)
    with col_select:
        period_option = st.selectbox(
            "보유기간 선택",
            options=[5, 10, 20],
            format_func=lambda x: f"{x}일 보유 기준",
            index=1,
            key="win_rate_period_select",
            label_visibility="collapsed"
        )

    col_name = f"{period_option}일 승률(%)"
    categories = summary["점수구간"].tolist()
    win_rates = summary.get(col_name, [0]*len(categories)).tolist()
    loss_rates = [max(0, 100 - w) for w in win_rates]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=categories, x=win_rates, name='익절(승)', orientation='h',
        marker=dict(
            color=COLOR_WIN, 
            cornerradius=4,
            line=dict(width=0)
        ),
        text=[f"{v:.1f}%" for v in win_rates], textposition='inside',
        textfont=dict(color="#FFFFFF", size=11, weight="bold")
    ))

    fig.add_trace(go.Bar(
        y=categories, x=loss_rates, name='손절(패)', orientation='h',
        marker=dict(
            color=COLOR_LOSS, 
            cornerradius=4,
            line=dict(width=0)
        ),
        text=[f"{v:.1f}%" for v in loss_rates], textposition='inside',
        textfont=dict(color="#0F172A", size=11, weight="bold")
    ))

    fig.update_layout(
        barmode='stack',
        bargap=0.32,
        height=240,
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, range=[0, 100], ticksuffix="%"),
        yaxis=dict(tickfont=dict(size=12, color=COLOR_TEXT_MAIN, weight="bold")),
        legend=dict(
            orientation="h", 
            yanchor="bottom", y=1.05, 
            xanchor="right", x=1,
            font=dict(size=11, color=COLOR_TEXT_SUB)
        )
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def _render_custom_table(summary):
    rows_html = ""
    for _, row in summary.iterrows():
        sample_cnt = row["표본수"]
        if sample_cnt >= MIN_RELIABLE_N:
            badge = f'<span class="badge-sample">{sample_cnt:,}건</span>'
        else:
            badge = f'<span class="badge-sample" style="background:#FEE2E2; color:#991B1B;">{sample_cnt:,}건 (미달)</span>'

        r5 = row.get('5일 평균수익률(%)', 0)
        r10 = row.get('10일 평균수익률(%)', 0)
        r20 = row.get('20일 평균수익률(%)', 0)

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

    st.html(f"""
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
    """)