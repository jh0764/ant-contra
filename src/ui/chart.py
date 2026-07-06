import json
import streamlit.components.v1 as components

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
            <div id="hoverDate" style="color:#9CA3AF; font-size:13px; margin-bottom:2px;"></div>
            <div id="hoverPrice" style="color:#FFFFFF; font-size:28px; font-weight:700;"></div>
          </div>
          <svg id="stockSvg" width="100%" height="430" viewBox="0 0 1000 430" preserveAspectRatio="xMidYMid meet"
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
 
            const W = 1000, H = 430;
            const padTop = 60, padBottom = 30, padX = 70;
 
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
    
    components.html(chart_html, height=450)