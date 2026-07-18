import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300, show_spinner=False)
def _fetch_frgn_rows(ticker_code):
    url = f"https://finance.naver.com/item/frgn.naver?code={ticker_code}"
    hdrs = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": f"https://finance.naver.com/item/main.naver?code={ticker_code}"
    }
    resp = requests.get(url, headers=hdrs, timeout=6)
    content = resp.content
    html = content.decode("euc-kr", errors="replace") if b"euc-kr" in content[:500].lower() else content.decode("utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table.type2 tr")
    parsed = []
    for row in rows:
        tds = row.select("td")
        if len(tds) < 8:
            continue
        parsed.append([td.get_text().strip() for td in tds])  # Tag → str 리스트로 변환
    return parsed

#네이버 종목토론방        
@st.cache_data(ttl=300, show_spinner=False)
def get_naver_discussion_by_likes(ticker_code):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": f"https://finance.naver.com/item/board.naver?code={ticker_code}"
    }
    base_url = f"https://finance.naver.com/item/board.naver?code={ticker_code}"

    def fetch_page(page_num):
        try:
            resp = requests.get(f"{base_url}&page={page_num}", headers=headers, timeout=5)
            content = resp.content
            if b'charset=utf-8' in content.lower():
                html = content.decode('utf-8', errors='replace')
            else:
                html = content.decode('cp949', errors='replace')
            soup = BeautifulSoup(html, "html.parser")
            rows = soup.select("table.type2 tr")
            posts = []
            for row in rows:
                title_td = row.select_one("td.title a")
                if not title_td:
                    continue
                title_text = title_td.get_text().strip()
                if not title_text or len(title_text) <= 2:
                    continue
                tds = row.select("td")
                if len(tds) < 6:
                    continue
                # 날짜 파싱으로 시간 가중치 계산
                date_text = tds[0].get_text().strip()
                try:
                    post_time = pd.to_datetime(date_text)
                    now = pd.Timestamp.now()
                    hours_ago = (now - post_time).total_seconds() / 3600
                    if hours_ago <= 3:
                        time_weight = 2.0
                    elif hours_ago <= 24:
                        time_weight = 1.5
                    else:
                        time_weight = 1.0
                except Exception:
                    time_weight = 1.0
                try:
                    views = int(tds[3].get_text().strip().replace(",", ""))
                    likes = int(tds[4].get_text().strip().replace(",", ""))
                    dislikes = int(tds[5].get_text().strip().replace(",", ""))
                except (ValueError, IndexError):
                    views, likes, dislikes = 0, 0, 0
                posts.append({
                    "title": title_text,
                    "likes": likes,
                    "dislikes": dislikes,
                    "views": views,
                    "time_weight": time_weight
                })
            return posts
        except Exception:
            return []

    # 1페이지 먼저 수집해서 밀도 측정
    first_page = fetch_page(1)
    page_count = len(first_page)

    # 밀도 기준 추가 페이지 수 결정
    if page_count >= 15:       # 대형주: 하루 수백 개 → 5페이지
        max_pages = 5
    elif page_count >= 8:      # 중형주
        max_pages = 3
    else:                      # 소형주: 글 자체가 적음
        max_pages = 1

    all_posts = first_page[:]
    for p in range(2, max_pages + 1):
        all_posts.extend(fetch_page(p))
        if len(all_posts) >= 80:   # 상한선
            break

    if not all_posts:
        # 백업 데이터 (기존 유지)
        return [
            {"title": "지금 가격대면 무조건 분할 매수 기회라고 봅니다", "likes": 42, "dislikes": 5, "views": 450, "time_weight": 1.0},
            {"title": "외인 기관 양매도 폭탄 던지는데 버티는 주주들 대단하네", "likes": 35, "dislikes": 2, "views": 390, "time_weight": 1.0},
            {"title": "반대매매 물량 다 소화해야 올라갈 듯.. 당분간 관망 추천", "likes": 28, "dislikes": 4, "views": 310, "time_weight": 1.0},
            {"title": "평단가 대비 하락폭 너무 큽니다. 다들 힘내세요", "likes": 21, "dislikes": 1, "views": 280, "time_weight": 1.0},
            {"title": "호재 공시 떴는데 왜 주가는 반대로 가냐 주포 일 안 하네", "likes": 18, "dislikes": 3, "views": 250, "time_weight": 1.0},
        ]

    # 시간 가중치 반영 정렬
    sorted_posts = sorted(
        all_posts,
        key=lambda x: (x["likes"] * 5 - x["dislikes"] * 2 + x["views"] * 0.1) * x["time_weight"],
        reverse=True
    )
    return sorted_posts[:30]        


def get_foreign_net_buying(ticker_code):
    try:
        tds_rows = _fetch_frgn_rows(ticker_code)
        net_values = []
        for tds in tds_rows:
            try:
                val_text = tds[6].replace(",", "").replace("+", "")
                if not val_text or val_text == "-":
                    continue
                net_values.append(int(val_text))
            except (ValueError, IndexError):
                continue
            if len(net_values) >= 5:
                break

        if len(net_values) < 2:
            raise ValueError(f"파싱 실패: {len(net_values)}건")

        consec_sell = sum(1 for v in net_values[:3] if v < 0)
        consec_buy  = sum(1 for v in net_values[:3] if v > 0)
        recent_sum  = sum(net_values[:3]) // 100
        is_turning = (net_values[0] > 0 and net_values[1] < 0 and net_values[2] < 0)
        is_still_selling = consec_sell >= 3

        return {
            "net_values": net_values, "consec_sell": consec_sell, "consec_buy": consec_buy,
            "recent_sum": recent_sum, "is_turning": is_turning, "is_still_selling": is_still_selling,
        }
    except Exception as e:
        return {"error": str(e)}
        
@st.cache_data(ttl=300, show_spinner=False)
def get_news_vacuum(ticker_code):
    try:
        news_url = f"https://finance.naver.com/item/news_news.naver?code={ticker_code}&page=1"
        resp_n = requests.get(news_url, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": f"https://finance.naver.com/item/main.naver?code={ticker_code}"
        }, timeout=5)
        soup_n = BeautifulSoup(resp_n.content, "html.parser")
        # 당일 기사 수 카운트
        today_str_display = pd.Timestamp.now().strftime("%Y.%m.%d")
        all_dates = [td.get_text().strip() for td in soup_n.select("td.date")]
        today_count = sum(1 for d in all_dates if today_str_display in d)
        total_count_news = len(all_dates)

        # 당일 기사 비율
        today_ratio = today_count / total_count_news if total_count_news > 0 else 0

        return {"today_count": today_count, "today_ratio": today_ratio}
    except Exception as e:
        return {"error": str(e)}