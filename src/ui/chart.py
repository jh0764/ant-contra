import json
import streamlit.components.v1 as components
import plotly.graph_objects as go
from constants import PRICE_COLOR, THEME, ACCENT
import streamlit as st
from ui.common import html_block
import pandas as pd
from urllib.parse import quote


def render_stock_chart(dates_korean, close_cleaned):
    max_idx = close_cleaned.idxmax()
    min_idx = close_cleaned.idxmin()
    
    chart_points = [
            {"date": str(d), "price": int(p)}
            for d, p in zip(dates_korean.tolist(), close_cleaned.tolist())
        ]
    
    chart_data_json = json.dumps(chart_points, ensure_ascii=False)
    max_point_idx = int(close_cleaned.reset_index(drop=True).idxmax())
    min_point_idx = int(close_cleaned.reset_index(drop=True).idxmin())
    
    chart_html = f"""
        <div id="stockChartWrap" style="position:relative; width:100%; font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;">
          <div id="hoverInfo" style="position:absolute; top:0px; left:50%; transform:translateX(-50%);
               text-align:center; pointer-events:none; z-index:5; opacity:0; transition:opacity 0.1s;">
            <div id="hoverDate" style="color:#6b7280; font-size:13px; margin-bottom:2px;"></div>
            <div id="hoverPrice" style="color:#1a1d29; font-size:28px; font-weight:700;"></div>
          </div>
          <svg id="stockSvg" width="100%" height="400" viewBox="0 0 1000 400" preserveAspectRatio="xMidYMid meet"
               style="display:block; cursor:crosshair;">
            <line id="spikeLine" x1="0" y1="0" x2="0" y2="430" stroke="rgba(255,255,255,0.35)"
                  stroke-width="1" style="display:none;" />
            <path id="priceLine" fill="none" stroke="#FF4B4B" stroke-width="2.5" />
            <circle id="hoverDot" r="5" fill="#FF4B4B" stroke="white" stroke-width="1.5" style="display:none;" />
            <circle id="maxDot" r="4.5" fill="#FF4B4B" stroke="white" stroke-width="1.5" />
            <circle id="minDot" r="4.5" fill="#FF4B4B" stroke="white" stroke-width="1.5" />
            <text id="maxLabel" fill="#FF6B6B" font-size="14" text-anchor="middle"></text>
            <text id="minLabel" fill="#FF6B6B" font-size="14" text-anchor="middle"></text>
          </svg>
        </div>
        <script>
        (function() {{
            const data = {chart_data_json};
            const maxIdx = {max_point_idx};
            const minIdx = {min_point_idx};
 
            const svg = document.getElementById("stockSvg");
            const pathEl = document.getElementById("priceLine");
            const spikeLine = document.getElementById("spikeLine");
            const hoverDot = document.getElementById("hoverDot");
            const hoverInfo = document.getElementById("hoverInfo");
            const hoverDate = document.getElementById("hoverDate");
            const hoverPrice = document.getElementById("hoverPrice");
            const maxDot = document.getElementById("maxDot");
            const minDot = document.getElementById("minDot");
            const maxLabel = document.getElementById("maxLabel");
            const minLabel = document.getElementById("minLabel");
 
            const W = 1000, H = 400;
            const padTop = 15, padBottom = 10, padX = 15;
 
            const prices = data.map(d => d.price);
            const minP = Math.min(...prices);
            const maxP = Math.max(...prices);
            const range = (maxP - minP) || 1;
 
            function xPos(i) {{
                if (data.length === 1) return W / 2;
                return padX + (i / (data.length - 1)) * (W - padX * 2);
            }}
            function yPos(price) {{
                const usableH = H - padTop - padBottom;
                return padTop + (1 - (price - minP) / range) * usableH;
            }}
 
 
            // 점이 차트 좌/우 가장자리 근처에 있으면 텍스트가 viewBox 밖으로 잘리므로
            // text-anchor를 동적으로 바꿔서 항상 차트 안쪽으로 텍스트가 뻗어나가도록 처리
            function anchorFor(x) {{
                if (x < padX + 40) return "start";   // 왼쪽 가장자리 → 점 기준 오른쪽으로 텍스트
                if (x > W - padX - 40) return "end";  // 오른쪽 가장자리 → 점 기준 왼쪽으로 텍스트
                return "middle";
            }}

            function redraw() {{
                let pathD = "";
                data.forEach((d, i) => {{
                    const x = xPos(i), y = yPos(d.price);
                    pathD += (i === 0 ? "M" : "L") + x.toFixed(2) + "," + y.toFixed(2) + " ";
                }});
                pathEl.setAttribute("d", pathD);

                const maxX = xPos(maxIdx), maxY = yPos(data[maxIdx].price);
                const minX = xPos(minIdx), minY = yPos(data[minIdx].price);
                maxDot.setAttribute("cx", maxX); maxDot.setAttribute("cy", maxY);
                minDot.setAttribute("cx", minX); minDot.setAttribute("cy", minY);

                maxLabel.setAttribute("x", maxX);
                maxLabel.setAttribute("y", Math.max(16, maxY - 16));
                maxLabel.setAttribute("text-anchor", anchorFor(maxX));
                maxLabel.textContent = "최고 " + data[maxIdx].price.toLocaleString() + "원";

                minLabel.setAttribute("x", minX);
                minLabel.setAttribute("y", Math.min(H - 6, minY + 24));
                minLabel.setAttribute("text-anchor", anchorFor(minX));
                minLabel.textContent = "최저 " + data[minIdx].price.toLocaleString() + "원";
            }}

            redraw();
            window.addEventListener("resize", redraw);
 
            function findNearestIndex(mouseX) {{
                let nearest = 0, minDist = Infinity;
                data.forEach((d, i) => {{
                    const dist = Math.abs(xPos(i) - mouseX);
                    if (dist < minDist) {{ minDist = dist; nearest = i; }}
                }});
                return nearest;
            }}
 
            function handleMove(evt) {{
                const rect = svg.getBoundingClientRect();
                const clientX = evt.touches ? evt.touches[0].clientX : evt.clientX;
                const relX = ((clientX - rect.left) / rect.width) * W;
                const idx = findNearestIndex(relX);
                const point = data[idx];
                const px = xPos(idx), py = yPos(point.price);
 
                spikeLine.setAttribute("x1", px);
                spikeLine.setAttribute("x2", px);
                spikeLine.style.display = "block";
 
                hoverDot.setAttribute("cx", px);
                hoverDot.setAttribute("cy", py);
                hoverDot.style.display = "block";
 
                hoverDate.textContent = point.date;
                hoverPrice.textContent = point.price.toLocaleString() + "원";
                hoverInfo.style.opacity = "1";
            }}
 
            function handleLeave() {{
                spikeLine.style.display = "none";
                hoverDot.style.display = "none";
                hoverInfo.style.opacity = "0";
            }}
 
            svg.addEventListener("mousemove", handleMove);
            svg.addEventListener("mouseleave", handleLeave);
            svg.addEventListener("touchmove", handleMove, {{passive: true}});
            svg.addEventListener("touchend", handleLeave);
        }})();
        </script>
        """
    
    components.html(chart_html, height=400)
    
def render_candle_chart(df, key_prefix="candle"):
    display_df = df.reset_index(drop=True)
    x_labels = display_df['Date'].dt.strftime('%m/%d')
    n = len(display_df)

    period_map = {"1개월": 21, "3개월": 63, "6개월": 126, "전체": n}
    period_labels = list(period_map.keys())

    qp_key = f"{key_prefix}_p"
    current = st.query_params.get(qp_key, "3개월")
    if current not in period_map:
        current = "3개월"

    stock_qp = quote(st.query_params.get("stock", ""), safe="")
    btns = "".join(
        f'<a href="?stock={stock_qp}&tab=candle&{qp_key}={quote(l, safe="")}" '
        f'class="pbtn {"on" if l==current else ""}">{l}</a>'
        for l in period_labels
    )

    html_block(f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin:4px 0 8px 0; flex-wrap:wrap; gap:8px;">
      <div style="display:flex; gap:12px; align-items:center;">
        <span style="display:flex; align-items:center; gap:5px; font-size:10.5px; color:{THEME['text_sub']};">
          <span style="width:14px; height:8px; background:rgba(240,68,82,0.25); border-radius:2px;"></span>일목구름대
        </span>
        <span style="display:flex; align-items:center; gap:5px; font-size:10.5px; color:{THEME['text_sub']};">
          <span style="width:14px; height:2px; background:#FF7A2F;"></span>VWAP(20)
        </span>
        <span style="display:flex; align-items:center; gap:5px; font-size:10.5px; color:{THEME['text_sub']};">
          <span style="width:14px; height:0; border-top:1.5px dashed #94a3b8;"></span>볼린저 밴드
        </span>
      </div>
      <div style="display:flex; gap:2px; background:{THEME['border']}55; padding:2px; border-radius:7px;">
        {btns}
      </div>
    </div>
    <style>
    .pbtn {{
      padding:2px 9px; font-size:9.5px; font-weight:600;
      border-radius:5px; color:{THEME['text_sub']};
      text-decoration:none; white-space:nowrap;
    }}
    .pbtn.on {{ background:{THEME['surface']}; color:{THEME['text_main']}; box-shadow:0 1px 2px rgba(0,0,0,0.15); }}
    .pbtn:visited {{ color:{THEME['text_sub']}; }}
    .pbtn.on:visited {{ color:{THEME['text_main']}; }}
    </style>
    """)

    selected_bars = period_map[current]
    start_idx = max(0, n - selected_bars)

    ma20 = display_df['Close'].rolling(20).mean()
    std20 = display_df['Close'].rolling(20).std()
    bb_upper = ma20 + 2 * std20
    bb_lower = ma20 - 2 * std20

    typical = (display_df['High'] + display_df['Low'] + display_df['Close']) / 3
    vwap20 = (typical * display_df['Volume']).rolling(20).sum() / display_df['Volume'].rolling(20).sum()

    conv = (display_df['High'].rolling(9).max() + display_df['Low'].rolling(9).min()) / 2
    base = (display_df['High'].rolling(26).max() + display_df['Low'].rolling(26).min()) / 2
    span_a = ((conv + base) / 2).shift(26)
    span_b = ((display_df['High'].rolling(52).max() + display_df['Low'].rolling(52).min()) / 2).shift(26)
    cloud_bull_a = span_a.where(span_a >= span_b)
    cloud_bull_b = span_b.where(span_a >= span_b)
    cloud_bear_a = span_a.where(span_a < span_b)
    cloud_bear_b = span_b.where(span_a < span_b)



    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=display_df['Date'],
        open=display_df['Open'], high=display_df['High'],
        low=display_df['Low'], close=display_df['Close'],
        increasing_line_color=PRICE_COLOR['up'], increasing_fillcolor=PRICE_COLOR['up'],
        decreasing_line_color=PRICE_COLOR['down'], decreasing_fillcolor=PRICE_COLOR['down'],
        line=dict(width=1),
        customdata=display_df[['Open', 'High', 'Low', 'Close']].values,
        hovertemplate=(
            "<b>%{x}</b><br>시가 %{customdata[0]:,.0f}원<br>고가 %{customdata[1]:,.0f}원"
            "<br>저가 %{customdata[2]:,.0f}원<br>종가 %{customdata[3]:,.0f}원<extra></extra>"
        ),
        name="", showlegend=False,
    ))
    fig.add_trace(go.Scatter(x=display_df['Date'], y=bb_upper, mode="lines", line=dict(color="#94a3b8", width=1, dash="dot"), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=display_df['Date'], y=bb_lower, mode="lines", line=dict(color="#94a3b8", width=1, dash="dot"), fill="tonexty", fillcolor="rgba(148,163,184,0.08)", hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=display_df['Date'], y=vwap20, mode="lines", line=dict(color="#FF7A2F", width=1.4), name="VWAP", hovertemplate="%{x}<br>VWAP %{y:,.0f}원<extra></extra>", showlegend=False))
    fig.add_trace(go.Scatter(x=display_df['Date'], y=cloud_bull_a, mode="lines", line=dict(color="rgba(240,68,82,0.35)", width=0.8), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=display_df['Date'], y=cloud_bull_b, mode="lines", line=dict(color="rgba(240,68,82,0.35)", width=0.8), fill="tonexty", fillcolor="rgba(240,68,82,0.12)", hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=display_df['Date'], y=cloud_bear_a, mode="lines", line=dict(color="rgba(49,130,246,0.35)", width=0.8), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=display_df['Date'], y=cloud_bear_b, mode="lines", line=dict(color="rgba(49,130,246,0.35)", width=0.8), fill="tonexty", fillcolor="rgba(148,163,184,0.10)", hoverinfo="skip", showlegend=False))

    y_min = float(display_df['Low'].iloc[start_idx:].min())
    y_max = float(display_df['High'].iloc[start_idx:].max())
    y_pad = (y_max - y_min) * 0.04

    fig.update_layout(
        height=400, margin=dict(l=0, r=20, t=8, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False,
        showlegend=False,
        font=dict(color=THEME['text_main'], size=11),
        bargap=0.45,
        hovermode="x unified",
        hoverlabel=dict(bgcolor=THEME['surface'], bordercolor=THEME['border'], font=dict(color=THEME['text_main'])),
        xaxis=dict(
            type='date',
            tickformat='%m/%d',
            showgrid=False, tickfont=dict(size=10.5),
            range=[display_df['Date'].iloc[start_idx], display_df['Date'].iloc[-1]],
        ),
        yaxis=dict(
            gridcolor=THEME['border'], gridwidth=1,
            tickformat=",.0f", ticksuffix="원",
            tickfont=dict(size=10.5),
            range=[y_min - y_pad, y_max + y_pad],
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})