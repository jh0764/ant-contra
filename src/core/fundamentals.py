import requests
from bs4 import BeautifulSoup

def get_fundamental_data(ticker_code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={ticker_code}"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": url}
        resp = requests.get(url, headers=headers, timeout=6)
        content = resp.content
        html = content.decode("euc-kr", errors="replace") if b"euc-kr" in content[:500].lower() else content.decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")

        market_cap_el = soup.select_one("#_market_sum")
        market_cap = market_cap_el.find_parent("td").get_text(" ", strip=True) if market_cap_el else "—"
        market_cap = " ".join(market_cap.split())   # 추가: 개행/중복공백 제거 → 코드블록 오인 방지
        
        def text(sel):
            el = soup.select_one(sel)
            return el.get_text(strip=True) if el else "—"

        per, eps, pbr = text("#_per"), text("#_eps"), text("#_pbr")

        div_yield = "—"
        for row in soup.select("table.per_table tr"):
            th = row.select_one("th")
            if th and "배당수익률" in th.get_text():
                td = row.select_one("td")
                div_yield = td.get_text(strip=True) if td else "—"
                break

        sector = "—"
        sector_el = soup.select_one(".trade_compare h4 a") or soup.select_one(".description a")
        if sector_el:
            sector = sector_el.get_text(strip=True)

        return {
            "market_cap": market_cap,
            "per": per, "pbr": pbr,
            "eps": f"{eps}원" if eps != "—" else "—",
            "dividend_yield": div_yield,
            "sector": sector,
        }
    except Exception:
        return {"market_cap": "—", "per": "—", "pbr": "—", "eps": "—", "dividend_yield": "—", "sector": "—"}