import json
import streamlit.components.v1 as components
import plotly.graph_objects as go
from constants import PRICE_COLOR, THEME, ACCENT
import streamlit as st
from ui.common import html_block
import pandas as pd
from ui.common import html_block, render_tab_group, render_flex_row


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
            <defs>
              <linearGradient id="lineFillGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#FF4B4B" stop-opacity="0.18"/>
                <stop offset="100%" stop-color="#FF4B4B" stop-opacity="0"/>
              </linearGradient>
            </defs>
            <g id="gridLines"></g>
            <line id="spikeLine" x1="0" y1="0" x2="0" y2="400" stroke="rgba(148,163,184,0.35)"
                  stroke-width="1" style="display:none;" />
            <path id="areaFill" fill="url(#lineFillGrad)" stroke="none" />
            <path id="priceLine" fill="none" stroke="#FF4B4B" stroke-width="2.6" stroke-linejoin="round" />
            <circle id="hoverDot" r="5" fill="#FF4B4B" stroke="white" stroke-width="1.5" style="display:none;" />
            <circle id="maxDot" r="4.5" fill="#FF4B4B" stroke="white" stroke-width="1.5" />
            <circle id="minDot" r="4.5" fill="#FF4B4B" stroke="white" stroke-width="1.5" />
            <text id="maxLabel" fill="#FF6B6B" font-size="13" font-weight="600" text-anchor="middle"></text>
            <text id="minLabel" fill="#FF6B6B" font-size="13" font-weight="600" text-anchor="middle"></text>
          </svg>
        </div>
        <script>
        (function() {{
            const data = {chart_data_json};
            const maxIdx = {max_point_idx};
            const minIdx = {min_point_idx};

            const svg = document.getElementById("stockSvg");
            const gridLines = document.getElementById("gridLines");
            const pathEl = document.getElementById("priceLine");
            const areaEl = document.getElementById("areaFill");
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
            const padTop = 30, padBottom = 30, padX = 60;

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

            function anchorFor(x) {{
                if (x < padX + 40) return "start";
                if (x > W - padX - 40) return "end";
                return "middle";
            }}

            function drawGrid() {{
                gridLines.innerHTML = "";
                const steps = 4;
                for (let i = 0; i <= steps; i++) {{
                    const price = minP + (range * i / steps);
                    const y = yPos(price);
                    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                    line.setAttribute("x1", padX);
                    line.setAttribute("x2", W - 10);
                    line.setAttribute("y1", y.toFixed(2));
                    line.setAttribute("y2", y.toFixed(2));
                    line.setAttribute("stroke", "rgba(148,163,184,0.18)");
                    line.setAttribute("stroke-width", "1");
                    gridLines.appendChild(line);

                    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    label.setAttribute("x", padX - 10);
                    label.setAttribute("y", (y + 4).toFixed(2));
                    label.setAttribute("text-anchor", "end");
                    label.setAttribute("font-size", "11");
                    label.setAttribute("fill", "#94a3b8");
                    label.textContent = Math.round(price).toLocaleString() + "원";
                    gridLines.appendChild(label);
                }}
            }}

            function redraw() {{
                let pathD = "";
                data.forEach((d, i) => {{
                    const x = xPos(i), y = yPos(d.price);
                    pathD += (i === 0 ? "M" : "L") + x.toFixed(2) + "," + y.toFixed(2) + " ";
                }});
                pathEl.setAttribute("d", pathD);

                const bottomY = H - padBottom;
                const areaD = pathD + `L ${{xPos(data.length - 1).toFixed(2)}},${{bottomY}} L ${{xPos(0).toFixed(2)}},${{bottomY}} Z`;
                areaEl.setAttribute("d", areaD);

                const maxX = xPos(maxIdx), maxY = yPos(data[maxIdx].price);
                const minX = xPos(minIdx), minY = yPos(data[minIdx].price);
                maxDot.setAttribute("cx", maxX); maxDot.setAttribute("cy", maxY);
                minDot.setAttribute("cx", minX); minDot.setAttribute("cy", minY);

                const labelsClose = Math.abs(maxY - minY) < 30 && Math.abs(maxX - minX) < 120;

                maxLabel.setAttribute("x", maxX);
                maxLabel.setAttribute("y", Math.max(16, maxY - 14));
                maxLabel.setAttribute("text-anchor", anchorFor(maxX));
                maxLabel.textContent = "최고 " + data[maxIdx].price.toLocaleString() + "원";

                minLabel.setAttribute("x", minX);
                minLabel.setAttribute("y", labelsClose ? Math.min(H - padBottom - 6, minY + 34) : Math.min(H - padBottom - 6, minY + 20));
                minLabel.setAttribute("text-anchor", anchorFor(minX));
                minLabel.textContent = "최저 " + data[minIdx].price.toLocaleString() + "원";

                drawGrid();
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
    n = len(display_df)

    period_map = {"1개월": 21, "3개월": 63, "6개월": 126, "전체": n}
    period_labels = list(period_map.keys())

    with render_flex_row(f"{key_prefix}_row", margin_bottom="4px"):
        html_block(f"""
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
        """)
        current = render_tab_group(period_labels, key=f"{key_prefix}_period_sel",
                                    default_index=1, size="sm", selected_color=THEME['text_main'],
                                    margin_bottom="-8px")

    selected_bars = period_map.get(current, period_map[period_labels[1]])
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