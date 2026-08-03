import math
from ui.common import html_block


def render_wave_gauge(
    score,
    label_top="통합 비명 지수",
    comment_text="역발상 매수 최적 구간 — 군중 공포 극대화",
    diff_text="전일과 동일",
):
    score_val = max(0, min(100, float(score)))

    if score_val >= 80:
        bg_badge = "#fee2e2"
        text_badge = "#dc2626"
        status_text = "극단적 공포"
    elif score_val >= 60:
        bg_badge = "#ffedd5"
        text_badge = "#ea580c"
        status_text = "공포"
    elif score_val >= 40:
        bg_badge = "#fef9c3"
        text_badge = "#ca8a04"
        status_text = "중립"
    elif score_val >= 20:
        bg_badge = "#ecfccb"
        text_badge = "#65a30d"
        status_text = "탐욕"
    else:
        bg_badge = "#dcfce7"
        text_badge = "#16a34a"
        status_text = "극단적 탐욕"

    cx, cy, r = 140, 125, 92
    angle_deg = 180 - (score_val / 100.0 * 180)
    angle_rad = math.radians(angle_deg)

    tip_x = cx + (r + 2) * math.cos(angle_rad)
    tip_y = cy - (r + 2) * math.sin(angle_rad)

    base_len = r + 15
    base_cx = cx + base_len * math.cos(angle_rad)
    base_cy = cy - base_len * math.sin(angle_rad)

    wing_r = 5.5
    p1_x = base_cx + wing_r * math.cos(angle_rad + math.pi / 2)
    p1_y = base_cy - wing_r * math.sin(angle_rad + math.pi / 2)
    p2_x = base_cx + wing_r * math.cos(angle_rad - math.pi / 2)
    p2_y = base_cy - wing_r * math.sin(angle_rad - math.pi / 2)

    html_block(
        f"""
<style>
    /* PC/데스크톱 화면에서는 영향이 없고, 768px 이하 모바일 모드에서만 위쪽에 18px 여백 부여 */
    @media (max-width: 768px) {{
        .wave-gauge-container {{
            margin-top: 18px !important;
        }}
    }}
</style>
<div class="wave-gauge-container" style="position:relative; overflow:hidden; background:rgba(255,255,255,0.4); border:1px solid rgba(255,255,255,0.6); border-radius:20px; padding:18px 16px; text-align:center; backdrop-filter:blur(20px) saturate(180%); -webkit-backdrop-filter:blur(20px) saturate(180%); box-shadow: 0 8px 24px rgba(31,38,135,0.08), inset 0 1px 0 rgba(255,255,255,0.9); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; box-sizing:border-box;">
    <div style="position:absolute; top:0; left:0; right:0; height:40%; background:linear-gradient(180deg, rgba(255,255,255,0.5) 0%, rgba(255,255,255,0) 100%); pointer-events:none;"></div>
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
            <path d="M 48 125 A 92 92 0 0 1 232 125" stroke="url(#softGaugeGrad)" stroke-width="17" fill="none" stroke-linecap="round"/>
            <polygon points="{tip_x:.1f},{tip_y:.1f} {p1_x:.1f},{p1_y:.1f} {p2_x:.1f},{p2_y:.1f}" fill="#1e293b" />
        </svg>

        <!-- 게이지 중앙 점수 (위치 정정: top 56px) -->
        <div style="position:absolute; top:56px; left:0; width:100%; text-align:center; pointer-events:none;">
            <span style="font-size:38px; font-weight:800; color:#111827; line-height:1; letter-spacing:-0.5px;">{int(score_val)}</span>
        </div>

        <!-- 하단 0 및 100 눈금 -->
        <div style="display:flex; justify-content:space-between; width:74%; margin:-10px auto 0 auto; font-size:11.5px; font-weight:600; color:#9ca3af;">
            <span>0</span>
            <span>100</span>
        </div>
    </div>

    <!-- 하단 코멘트 영역 -->
    <div style="margin-top:12px; padding-top:12px; border-top:1px solid #f3f4f6;">
        <div style="background:{bg_badge}; border-radius:10px; padding:4px 10px; display:inline-block; margin-bottom:6px;">
            <span style="font-size:11.5px; font-weight:700; color:{text_badge};">{status_text}</span>
        </div>
        <div style="font-size:12px; font-weight:500; color:#4b5563; margin-bottom:3px; word-break:keep-all; line-height:1.35; letter-spacing:-0.2px;">
            {comment_text}
        </div>
        <div style="font-size:11px; font-weight:400; color:#9ca3af;">
            {diff_text}
        </div>
    </div>
</div>
"""
    )
