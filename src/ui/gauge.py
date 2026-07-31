import math
from ui.common import html_block

def render_wave_gauge(score, label_top="통합 비명 지수", comment_text="역발상 매수 최적 구간 — 군중 공포 극대화", diff_text="전일과 동일"):
    # 1. 점수 범위 제한 (0 ~ 100)
    score_val = max(0, min(100, float(score)))

    # 2. 5단계 색상 및 상태 라벨
    if score_val >= 80:
        bg_badge = "#fee2e2"
        text_badge = "#dc2626"
        status_text = "극단적 공포"
        status_emoji = "🔥"
    elif score_val >= 60:
        bg_badge = "#ffedd5"
        text_badge = "#ea580c"
        status_text = "공포"
        status_emoji = "😨"
    elif score_val >= 40:
        bg_badge = "#fef9c3"
        text_badge = "#ca8a04"
        status_text = "중립"
        status_emoji = "😐"
    elif score_val >= 20:
        bg_badge = "#ecfccb"
        text_badge = "#65a30d"
        status_text = "탐욕"
        status_emoji = "🤑"
    else:
        bg_badge = "#dcfce7"
        text_badge = "#16a34a"
        status_text = "극단적 탐욕"
        status_emoji = "🚀"

    # 3. 삼각 화살표 좌표 계산 (SVG viewBox: 0 0 280 145, 중심 140,125, 반지름 92)
    cx, cy, r = 140, 125, 92
    angle_deg = 180 - (score_val / 100.0 * 180)
    angle_rad = math.radians(angle_deg)

    # 삼각 지시침 좌표
    tip_x = cx + (r + 2) * math.cos(angle_rad)
    tip_y = cy - (r + 2) * math.sin(angle_rad)

    base_len = r + 15
    base_cx = cx + base_len * math.cos(angle_rad)
    base_cy = cy - base_len * math.sin(angle_rad)

    wing_r = 5.5
    p1_x = base_cx + wing_r * math.cos(angle_rad + math.pi/2)
    p1_y = base_cy - wing_r * math.sin(angle_rad + math.pi/2)
    p2_x = base_cx + wing_r * math.cos(angle_rad - math.pi/2)
    p2_y = base_cy - wing_r * math.sin(angle_rad - math.pi/2)

    # 4. 균형을 정밀 재조정한 HTML/CSS 구조
    html_block(f"""
<div style="background:#ffffff; border:1px solid #f3f4f6; border-radius:20px; padding:18px 16px; text-align:center; box-shadow: 0 4px 18px rgba(0,0,0,0.03); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; box-sizing:border-box;">
    <!-- 상단 타이틀 -->
    <div style="font-size:14px; font-weight:700; color:#111827; margin-bottom:10px; text-align:left; padding-left:2px;">{label_top}</div>
    
    <!-- 게이지 메인 컨테이너 -->
    <div style="position:relative; width:100%; max-width:250px; margin:0 auto;">
        <!-- 매끄러운 단일 아크 게이지 & 바늘 -->
        <svg viewBox="0 0 280 145" width="100%" height="auto" style="display:block;">
            <defs>
                <linearGradient id="softGaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#4ade80"/>
                    <stop offset="25%" stop-color="#a3e635"/>
                    <stop offset="50%" stop-color="#facc15"/>
                    <stop offset="75%" stop-color="#fb923c"/>
                    <stop offset="100%" stop-color="#f87171"/>
                </linearGradient>
            </defs>
            <!-- 아크 바 -->
            <path d="M 48 125 A 92 92 0 0 1 232 125" stroke="url(#softGaugeGrad)" stroke-width="17" fill="none" stroke-linecap="round"/>

            <!-- 삼각 화살표 바늘 -->
            <polygon points="{tip_x:.1f},{tip_y:.1f} {p1_x:.1f},{p1_y:.1f} {p2_x:.1f},{p2_y:.1f}" fill="#1e293b" />
        </svg>

        <!-- 게이지 중앙 점수 -->
        <div style="position:absolute; top:42px; left:0; width:100%; text-align:center; pointer-events:none;">
            <span style="font-size:38px; font-weight:800; color:#111827; line-height:1; letter-spacing:-0.5px;">{int(score_val)}</span>
        </div>

        <!-- 하단 0 및 100 눈금 -->
        <div style="display:flex; justify-content:space-between; width:74%; margin:-10px auto 0 auto; font-size:11.5px; font-weight:600; color:#9ca3af;">
            <span>0</span>
            <span>100</span>
        </div>
    </div>

    <!-- 하단 코멘트 영역 (비율 최적화) -->
    <div style="margin-top:12px; padding-top:12px; border-top:1px solid #f3f4f6;">
        <!-- 상태 배지 -->
        <div style="background:{bg_badge}; border-radius:10px; padding:4px 10px; display:inline-block; margin-bottom:6px;">
            <span style="font-size:11.5px; font-weight:700; color:{text_badge};">{status_emoji} {status_text}</span>
        </div>
        <!-- 코멘트 텍스트 (크기 축소 및 비율 조정) -->
        <div style="font-size:12px; font-weight:500; color:#4b5563; margin-bottom:3px; word-break:keep-all; line-height:1.35; letter-spacing:-0.2px;">
            {comment_text}
        </div>
        <!-- 전일 대비 텍스트 -->
        <div style="font-size:11px; font-weight:400; color:#9ca3af;">
            {diff_text}
        </div>
    </div>
</div>
""")