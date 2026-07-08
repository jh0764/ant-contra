import math
from ui.common import html_block

def render_wave_gauge(score, label_top="통합 비명 지수"):
    if score >= 70: num_color = "#ef4444"
    elif score >= 55: num_color = "#f97316"
    elif score >= 35: num_color = "#1a1d29"
    else: num_color = "#22c55e"
    cx, cy, r = 150, 150, 120
    rad = math.radians(180 - 180 * (score / 100))
    nx, ny = cx + r * math.cos(rad), cy - r * math.sin(rad)
    arc_len = 377 * (score / 100)

    html_block(f"""
<div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:14px; padding:20px; text-align:center;">
<div style="font-size:13px; color:#6b7280; margin-bottom:8px;">{label_top}</div>
<svg viewBox="0 0 300 170" width="100%" height="170">
<defs>
<linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="#22c55e"/><stop offset="35%" stop-color="#eab308"/>
<stop offset="65%" stop-color="#f97316"/><stop offset="100%" stop-color="#ef4444"/>
</linearGradient>
</defs>
<path d="M 30 150 A 120 120 0 0 1 270 150" stroke="#f1f5f9" stroke-width="18" fill="none" stroke-linecap="round"/>
<path d="M 30 150 A 120 120 0 0 1 270 150" stroke="url(#gaugeGrad)" stroke-width="18" fill="none"
 stroke-linecap="round" stroke-dasharray="{arc_len:.1f} 377"/>
<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#1a1d29" stroke-width="4" stroke-linecap="round"/>
<circle cx="{cx}" cy="{cy}" r="6" fill="#1a1d29"/>
</svg>
<div style="font-size:44px; font-weight:800; color:{num_color}; margin-top:-10px;">{score}</div>
</div>
""")