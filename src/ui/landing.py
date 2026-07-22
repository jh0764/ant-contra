import streamlit as st
from constants import THEME

def render_landing():
    st.markdown(f"""
    <div style="text-align:center; padding: 60px 20px 40px 20px;">
      <div style="font-size:56px; margin-bottom:16px;">🤖</div>
      <h1 style="font-size:32px; font-weight:800; color:{THEME['text_main']}; margin-bottom:8px;">
        개미반대로
      </h1>
      <p style="font-size:16px; color:{THEME['text_sub']}; margin-bottom:4px;">
        군중이 공포에 떨 때, 숫자는 기회를 말한다
      </p>
      <p style="font-size:13px; color:{THEME['text_sub']}; margin-bottom:40px;">
        네이버 실시간 주주 여론 × 보조지표 × 수급 데이터 통합 역발상 스캐너
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin-bottom:48px;">
      <div style="background:#0f172a; border:1px solid #1e293b; border-radius:12px;
           padding:20px 24px; text-align:center; min-width:140px;">
        <div style="font-size:28px; font-weight:800; color:#ef4444;">😱</div>
        <div style="font-size:12px; color:#94a3b8; margin-top:6px;">통합 비명 지수</div>
        <div style="font-size:11px; color:#475569;">공포 구간 자동 감지</div>
      </div>
      <div style="background:#0f172a; border:1px solid #1e293b; border-radius:12px;
           padding:20px 24px; text-align:center; min-width:140px;">
        <div style="font-size:28px; font-weight:800; color:#22c55e;">📊</div>
        <div style="font-size:12px; color:#94a3b8; margin-top:6px;">객관 지표 분석</div>
        <div style="font-size:11px; color:#475569;">RSI · 볼린저 · 수급</div>
      </div>
      <div style="background:#0f172a; border:1px solid #1e293b; border-radius:12px;
           padding:20px 24px; text-align:center; min-width:140px;">
        <div style="font-size:28px; font-weight:800; color:#f59e0b;">🔥</div>
        <div style="font-size:12px; color:#94a3b8; margin-top:6px;">개미 관심도</div>
        <div style="font-size:11px; color:#475569;">FOMO 과열 탐지</div>
      </div>
      <div style="background:#0f172a; border:1px solid #1e293b; border-radius:12px;
           padding:20px 24px; text-align:center; min-width:140px;">
        <div style="font-size:28px; font-weight:800; color:#818cf8;">💬</div>
        <div style="font-size:12px; color:#94a3b8; margin-top:6px;">실시간 여론</div>
        <div style="font-size:11px; color:#475569;">네이버 토론방 분석</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-bottom:8px;">
      <span style="font-size:13px; color:#64748b;">
        ⚠️ 본 서비스는 투자 참고용이며, 투자 판단의 최종 책임은 본인에게 있습니다
      </span>
    </div>
    """, unsafe_allow_html=True)