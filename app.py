import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from streamlit_searchbox import st_searchbox
import FinanceDataReader as fdr
import random
import json
import numpy as np
 
# 1. Page Configuration
st.set_page_config(layout="wide", page_title="개미반대로 (Ant-Contra)")
 
st.title("🤖 개미반대로 (Ant-Contra)")
st.caption("네이버 실시간 추천 인기글")
st.markdown("---")
 
# ── 전체 상장 종목 리스트 로드 (KOSPI + KOSDAQ + KONEX 전체) ──────────
@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)  # 12시간마다 갱신
def load_krx_listing():
    """
    FinanceDataReader를 통해 한국거래소(KRX)에 상장된 전체 종목(코스피+코스닥+코넥스)
    리스트를 불러옵니다. fdr 버전에 따라 컬럼명이 'Code'/'Symbol', 'Name' 등으로
    달라질 수 있어 후보 컬럼명을 순서대로 시도합니다.
    실패 시 KRX(KIND) 공식 상장종목 다운로드 URL을 2차 백업으로 사용합니다.
    """
    code_candidates = ["Code", "Symbol", "종목코드"]
    name_candidates = ["Name", "회사명", "종목명"]
 
    def pick_column(columns, candidates):
        for c in candidates:
            if c in columns:
                return c
        return None
 
    # 1차: FinanceDataReader 시도
    try:
        listing = fdr.StockListing('KRX')
        code_col = pick_column(listing.columns, code_candidates)
        name_col = pick_column(listing.columns, name_candidates)
        if code_col is None or name_col is None:
            raise KeyError(f"컬럼을 찾을 수 없음: {list(listing.columns)}")
        listing = listing[[code_col, name_col]].rename(columns={code_col: "Code", name_col: "Name"})
        listing = listing.dropna(subset=["Code", "Name"])
        listing["Code"] = listing["Code"].astype(str).str.zfill(6)
        if len(listing) > 100:  # 정상적으로 전체 종목이 들어왔는지 최소한의 검증
            return listing, "fdr", None
    except Exception as e1:
        fdr_error = str(e1)
    else:
        fdr_error = "결과가 비정상적으로 적음"
 
    # 2차: KRX(KIND) 상장법인 목록 직접 다운로드 (fdr이 내부적으로 쓰는 것과 동일한 소스)
    try:
        url = "http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"
        raw = pd.read_html(url, header=0, encoding="euc-kr")[0]
        raw = raw[["회사명", "종목코드"]].rename(columns={"회사명": "Name", "종목코드": "Code"})
        raw["Code"] = raw["Code"].astype(str).str.zfill(6)
        raw = raw.dropna(subset=["Code", "Name"])
        if len(raw) > 100:
            return raw, "krx_kind", None
    except Exception as e2:
        kind_error = str(e2)
    else:
        kind_error = "결과가 비정상적으로 적음"
 
    # 3차: 둘 다 실패 시 최소 백업 리스트 (자주 검색되는 대형주 위주)
    backup = {
        "삼성전자": "005930", "삼성전자우": "005935", "SK하이닉스": "000660", "NAVER": "035420",
        "카카오": "035720", "LG에너지솔루션": "373220", "삼성바이오로직스": "207940",
        "현대차": "005380", "기아": "000270", "셀트리온": "068270", "POSCO홀딩스": "005490",
        "LG화학": "051910", "삼성SDI": "006400", "현대모비스": "012330", "KB금융": "105560",
        "신한지주": "055550", "삼성물산": "028260", "한화에어로스페이스": "012450",
        "두산에너빌리티": "034020", "삼성생명": "032830"
    }
    backup_df = pd.DataFrame({"Name": list(backup.keys()), "Code": list(backup.values())})
    error_msg = f"fdr 실패: {fdr_error} / KRX 백업 실패: {kind_error}"
    return backup_df, "backup", error_msg
 
KRX_LISTING, KRX_SOURCE, KRX_ERROR = load_krx_listing()
 
if KRX_SOURCE == "backup":
    st.warning(
        f"⚠️ 전체 종목 리스트를 불러오지 못해 주요 종목 {len(KRX_LISTING)}개만 검색 가능한 상태입니다. "
        "잠시 후 새로고침하면 정상화될 수 있습니다."
    )
 
# Company Search Function (전체 상장 종목 대상 부분일치 검색, 종목명/종목코드 모두 지원)
def search_companies(search_term):
    if not search_term or len(search_term) < 1:
        return []
 
    term = search_term.strip().lower()
 
    if KRX_LISTING.empty:
        return []
 
    # 종목명에 검색어가 포함되거나, 종목코드가 검색어로 시작하는 경우 모두 매칭
    name_match = KRX_LISTING["Name"].str.lower().str.contains(term, na=False, regex=False)
    code_match = KRX_LISTING["Code"].str.startswith(term, na=False)
    matched = KRX_LISTING[name_match | code_match]
 
    # 검색어로 시작하는 종목명을 우선순위로 정렬 (예: "삼성" 검색 시 "삼성전자"가 상단에)
    starts_with = matched["Name"].str.lower().str.startswith(term)
    matched = pd.concat([matched[starts_with], matched[~starts_with]])
 
    matched = matched.head(30)  # 너무 많으면 드롭다운이 무거워지므로 상위 30개로 제한
    return [f"{row['Name']} ({row['Code']})" for _, row in matched.iterrows()]
 
#네이버 종목토론방        
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

#감성 사전
def analyze_combined_sentiment(naver_posts, close_series=None, high_series=None, low_series=None):
    naver_titles = [p["title"] for p in naver_posts]
    all_texts = naver_titles  # DC 삭제됐으므로 네이버만
    total_analyzed_posts = max(1, len(all_texts))
    combined = " ".join(all_texts).lower()

    fear_dictionary = [
        # 기존
        "망", "살려", "물림", "한강", "상폐", "돔황챠", "지옥", "폭락", "녹는다",
        "손절", "개미무덤", "반대매매", "탈출은", "지하", "무섭", "피눈물",
        # 신규 추가
        "뇌동매매", "존버실패", "깡통", "반토막", "개잡주", "쓰레기", "작전주",
        "상장폐지", "허매수", "허매도", "뻥튀기", "개미털기", "세력먹튀",
        "풀매도", "탈출각", "손절각", "물타다", "존버불가", "멘탈터짐",
        "패닉", "급락", "하한가", "연속하락", "외인매도", "기관매도",
        "공매도폭탄", "빚투", "미수", "깡통계좌", "던지다", "패닉셀",
        "투매", "공포", "버티기힘", "저점모름", "끝없이", "무릎꿇",
        "손실", "손해", "파산", "청산", "강제청산", "마진콜", "눈물"
    ]
    greedy_dictionary = [
        # 기존
        "가즈아", "풀매수", "떡상", "돈복사", "상한가", "개추", "호재",
        "날아가", "수익", "수출대박", "돈벌", "인생역전", "매수기회",
        # 신규 추가
        "떡상각", "눌림목", "저점매수", "세력유입", "기관매수", "외인매수",
        "양봉", "거래량폭발", "목표가", "상향", "신고가", "돌파", "급등",
        "눌림", "담아가", "물량털기끝", "추가매수", "풀배팅", "올라간다",
        "저점확인", "반등", "회복", "턴어라운드", "바닥확인", "매집완료",
        "수급좋다", "외인유입", "기관유입", "대량매수", "쌍바닥"
    ]

    fear_hits = sum(1 for w in fear_dictionary if w in combined)
    greedy_hits = sum(1 for w in greedy_dictionary if w in combined)

    naver_weighted_fear = 0
    naver_weighted_greedy = 0
    for post in naver_posts:
        title = post["title"].lower()
        tw = post.get("time_weight", 1.0)
        post_weight = min(10, max(1, post["likes"] // 10)) * tw
        f_count = sum(1 for w in fear_dictionary if w in title)
        g_count = sum(1 for w in greedy_dictionary if w in title)
        naver_weighted_fear += f_count * post_weight
        naver_weighted_greedy += g_count * post_weight

    normalized_fear = (fear_hits * 6 + naver_weighted_fear * 3) / total_analyzed_posts
    normalized_greedy = (greedy_hits * 5 + naver_weighted_greedy * 2.5) / total_analyzed_posts

    # ── ATR 변동성 필터 ───────────────────────────────────────────
    volatility_warning = None
    sentiment_weight = 0.20  # 기본 커뮤니티 비중 20%

    if close_series is not None and len(close_series) >= 10:
        try:
            # True Range = max(H-L, |H-PC|, |L-PC|)
            if high_series is not None and low_series is not None and len(high_series) >= 10:
                prev_close = close_series.shift(1)
                tr = pd.concat([
                    high_series - low_series,
                    (high_series - prev_close).abs(),
                    (low_series  - prev_close).abs()
                ], axis=1).max(axis=1)
            else:
                # H/L 없을 때 폴백: 종가 기반 근사 (기존보다는 나음)
                tr = close_series.diff().abs()

            atr5  = float(tr.iloc[-5:].mean())
            atr20 = float(tr.iloc[-20:].mean()) if len(close_series) >= 20 else atr5
            atr_ratio = atr5 / atr20 if atr20 > 0 else 1.0

            if atr_ratio >= 2.0:
                sentiment_weight = 0.12  # 변동성 과열 시 감성 비중 축소
                volatility_warning = f"⚡ 변동성 과열 ({atr_ratio:.1f}배) — 감성 신뢰도 저하, 커뮤니티 가중치 자동 축소"
            elif atr_ratio >= 1.5:
                sentiment_weight = 0.16
                volatility_warning = f"⚠️ 변동성 확대 ({atr_ratio:.1f}배) — 감성 신뢰도 주의"
        except Exception:
            pass

    base_score = 50
    score_offset = (normalized_fear * 15) - (normalized_greedy * 12)
    raw_score = max(5, min(95, base_score + score_offset))
    # 교체
    community_score = int(raw_score * sentiment_weight)

    if raw_score >= 70:
        reason = f"공포 밀도({normalized_fear:.1f}) 높음. 추천글 대부분 투매·하락에 공감."
    elif raw_score <= 35:
        reason = f"탐욕 밀도({normalized_greedy:.1f}) 우세. FOMO·추격매수 여론 과도."
    else:
        reason = f"공포({normalized_fear:.1f})·탐욕({normalized_greedy:.1f}) 중립 구간."

    return int(raw_score), reason, community_score, volatility_warning



# ── 객관 지표 계산 함수 (가격 기반 40% + 수급 기반 30%) ──────────────
def calculate_objective_indicators(close_series, volume_series, ticker_code, high_series=None, low_series=None, is_kosdaq=False):
    """
    RSI, 볼린저 밴드, 52주 신저가 근접도, 거래량 폭발, 외국인 순매수를
    계산하여 각 지표의 상태와 점수를 반환합니다.
    """
    results = {}
    try:
        matched = KRX_LISTING[KRX_LISTING["Code"] == ticker_code]
        # yf suffix 기반 판별이 가장 정확하나 여기선 fdr 데이터 활용
        # fdr StockListing에 Market 컬럼 있으면 활용, 없으면 코드 범위로 간이 판별
        if "Market" in KRX_LISTING.columns and not matched.empty:
            is_kosdaq = str(matched["Market"].iloc[0]).upper() in ("KOSDAQ", "코스닥")
        else:
            code_int = int(ticker_code)
            # KOSDAQ 종목코드는 통상 0으로 시작하는 6자리 중 특정 범위
            # 완벽하진 않지만 yf .KQ suffix 시도 결과로 판별하는 게 더 정확
            is_kosdaq = False  # 기본값, 아래 yf suffix 판별로 보완
    except Exception:
        is_kosdaq = False
    # ── 1. RSI (14일) ─────────────────────────────────────────────
    try:
        delta = close_series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-9)
        rsi_val = float(100 - (100 / (1 + rs.iloc[-1])))
 
        if rsi_val <= 30:
            rsi_status = "green"
            rsi_label = f"RSI {rsi_val:.1f} — 과매도 극단 구간"
            rsi_desc = "통계적 바닥 근접. 역발상 매수 우위 신호"
            rsi_score = 15
        elif rsi_val <= 45:
            rsi_status = "yellow"
            rsi_label = f"RSI {rsi_val:.1f} — 약세 회복 구간"
            rsi_desc = "과매도 직후 회복 중. 추이 관찰 필요"
            rsi_score = 7
        elif rsi_val >= 70:
            rsi_status = "red"
            rsi_label = f"RSI {rsi_val:.1f} — 과매수 과열 구간"
            rsi_desc = "단기 고점 가능성. 역발상 매수 불리"
            rsi_score = -5
        else:
            rsi_status = "yellow"
            rsi_label = f"RSI {rsi_val:.1f} — 중립 구간"
            rsi_desc = "과매도·과매수 어느 쪽도 아님. 대기"
            rsi_score = 0
        results["rsi"] = {"status": rsi_status, "label": rsi_label, "desc": rsi_desc, "score": rsi_score, "value": rsi_val}
    except Exception:
        results["rsi"] = {"status": "yellow", "label": "RSI — 계산 불가", "desc": "데이터 부족", "score": 0, "value": None}
 
    # ── 2. 볼린저 밴드 (20일, 2σ) ──────────────────────────────────
    try:
        ma20 = close_series.rolling(20).mean()
        std20 = close_series.rolling(20).std()
        upper = ma20 + 2 * std20
        lower = ma20 - 2 * std20
        current = float(close_series.iloc[-1])
        lower_val = float(lower.iloc[-1])
        upper_val = float(upper.iloc[-1])
        ma_val = float(ma20.iloc[-1])
        band_width = upper_val - lower_val
        position_pct = ((current - lower_val) / band_width * 100) if band_width > 0 else 50
 
        if current <= lower_val:
            bb_status = "green"
            bb_label = f"볼린저 하단 이탈 ({position_pct:.0f}%)"
            bb_desc = "통계적으로 2.3%만 해당하는 극단 하락 구간"
            bb_score = 15
        elif position_pct <= 25:
            bb_status = "green"
            bb_label = f"볼린저 하단 근접 ({position_pct:.0f}%)"
            bb_desc = "하단 밴드 근접 중. 반등 가능성 높은 구간"
            bb_score = 8
        elif position_pct >= 80:
            bb_status = "red"
            bb_label = f"볼린저 상단 근접 ({position_pct:.0f}%)"
            bb_desc = "상단 밴드 근접. 단기 과열 구간"
            bb_score = -5
        else:
            bb_status = "yellow"
            bb_label = f"볼린저 중립 구간 ({position_pct:.0f}%)"
            bb_desc = "밴드 중간 위치. 방향성 대기 중"
            bb_score = 0
        results["bb"] = {"status": bb_status, "label": bb_label, "desc": bb_desc, "score": bb_score}
    except Exception:
        results["bb"] = {"status": "yellow", "label": "볼린저 밴드 — 계산 불가", "desc": "데이터 부족", "score": 0}
 
    # ── 3. 52주 신저가/신고가 근접도 (양방향) ─────────────────────────
    try:
        week52_low = float(close_series.min())
        week52_high = float(close_series.max())
        current = float(close_series.iloc[-1])
        gap_from_low_pct = ((current - week52_low) / week52_low) * 100
        gap_from_high_pct = ((week52_high - current) / week52_high) * 100

        if gap_from_low_pct <= 5:
            w52_status, w52_label = "green", f"52주 신저가 +{gap_from_low_pct:.1f}%"
            w52_desc, w52_score   = "신저가 5% 이내. 역발상 매수 최적 구간", 12
        elif gap_from_high_pct <= 3:
            w52_status, w52_label = "red", f"52주 신고가 근접 (-{gap_from_high_pct:.1f}%)"
            w52_desc, w52_score   = "신고가 구간. 공포 아닌 과열 국면. 추격 위험", -10
        elif gap_from_low_pct <= 15:
            w52_status, w52_label = "yellow", f"52주 저가 +{gap_from_low_pct:.1f}%"
            w52_desc, w52_score   = "저점 영역 내 위치", 4
        else:
            w52_status, w52_label = "yellow", f"52주 고가 대비 -{gap_from_high_pct:.1f}%"
            w52_desc, w52_score   = "중립 구간", 0
        results["w52"] = {"status": w52_status, "label": w52_label, "desc": w52_desc, "score": w52_score}
    except Exception:
        results["w52"] = {"status": "yellow", "label": "52주 데이터 — 계산 불가", "desc": "데이터 부족", "score": 0}

# ── 3-1. 고점 대비 낙폭 (Drawdown from 52W High) ─────────────
    try:
        week52_high = float(close_series.max())
        current     = float(close_series.iloc[-1])
        drawdown_pct = (week52_high - current) / week52_high * 100

        if drawdown_pct >= 40:
            dd_status, dd_label = "green", f"고점 대비 -{drawdown_pct:.1f}% (대낙폭)"
            dd_desc, dd_score   = "장기 투자자 손실 구간. 역발상 유효", 15
        elif drawdown_pct >= 25:
            dd_status, dd_label = "green", f"고점 대비 -{drawdown_pct:.1f}%"
            dd_desc, dd_score   = "유의미한 조정 구간", 8
        elif drawdown_pct >= 15:
            dd_status, dd_label = "yellow", f"고점 대비 -{drawdown_pct:.1f}%"
            dd_desc, dd_score   = "중간 조정. 추세 확인 필요", 3
        elif drawdown_pct <= 5:
            dd_status, dd_label = "red", f"고점 근접 -{drawdown_pct:.1f}%"
            dd_desc, dd_score   = "신고가 부근. 역발상 불리", -10
        else:
            dd_status, dd_label = "yellow", f"고점 대비 -{drawdown_pct:.1f}%"
            dd_desc, dd_score   = "중립 구간", 0

        results["drawdown"] = {
            "status": dd_status, "label": dd_label,
            "desc": dd_desc, "score": dd_score, "value": drawdown_pct
        }
    except Exception:
        results["drawdown"] = {"status": "yellow", "label": "낙폭 — 계산 불가",
                               "desc": "데이터 부족", "score": 0, "value": 0}

# ── 3-2. 일목균형표 구름대 이탈 ─────────────────────
    try:
        if high_series is not None and low_series is not None and len(close_series) >= 78:
            conv = (high_series.rolling(9).max() + low_series.rolling(9).min()) / 2
            base = (high_series.rolling(26).max() + low_series.rolling(26).min()) / 2
            span_a = ((conv + base) / 2).shift(26)
            span_b = ((high_series.rolling(52).max() + low_series.rolling(52).min()) / 2).shift(26)

            cloud_top = float(max(span_a.iloc[-1], span_b.iloc[-1]))
            cloud_bottom = float(min(span_a.iloc[-1], span_b.iloc[-1]))
            current = float(close_series.iloc[-1])

            if current < cloud_bottom:
                depth_pct = (cloud_bottom - current) / cloud_bottom * 100
                ich_status, ich_label = "green", f"구름대 하단 이탈 (-{depth_pct:.1f}%)"
                ich_desc, ich_score   = "구조적 하락 국면. 역발상 관찰 구간", min(12, 4 + depth_pct)
            elif current > cloud_top:
                ich_status, ich_label = "red", "구름대 상단 위 (추세 상승)"
                ich_desc, ich_score   = "구조적 상승 국면. 역발상 불리", -6
            else:
                ich_status, ich_label = "yellow", "구름대 내부 (혼조)"
                ich_desc, ich_score   = "추세 방향성 불명확", 0

            results["ichimoku"] = {"status": ich_status, "label": ich_label, "desc": ich_desc, "score": int(ich_score)}
        else:
            raise ValueError("데이터 부족")
    except Exception:
        results["ichimoku"] = {"status": "yellow", "label": "일목균형표 — 계산 불가", "desc": "데이터 부족", "score": 0}

# ── 4. 거래량 + 거래대금 결합 수급 강도 ──────────────────────
    try:
        vol_today    = float(volume_series.iloc[-1])
        vol_avg20    = float(volume_series.rolling(20).mean().iloc[-1])
        vol_ratio    = vol_today / vol_avg20 if vol_avg20 > 0 else 1.0
        price_today  = float(close_series.iloc[-1])
        price_prev   = float(close_series.iloc[-2])
        price_chg    = (price_today - price_prev) / price_prev

        # 거래대금(억) = 거래량 × 현재가 / 1억
        turnover_today  = vol_today * price_today / 1e8
        turnover_avg20  = vol_avg20 * price_today / 1e8
        turnover_ratio  = vol_ratio  # 거래대금 비율은 vol_ratio와 동일(가격 공통)

        # 거래대금 절대값 기준: 10억 미만 = 소형주 필터
        is_micro = turnover_today < 10

        # 수급 강도 = 거래량배수(60%) + 거래대금 절대크기(40%) 결합
        # 소형주는 배수 과대 방지를 위해 vol_ratio 상한 3배로 cap
        capped_ratio = min(vol_ratio, 3.0) if is_micro else vol_ratio

        if capped_ratio >= 2.0 and price_chg < -0.01:
            vol_status = "green"
            vol_label  = f"거래량 {capped_ratio:.1f}배 + 하락 — 투매 ({turnover_today:.0f}억)"
            vol_desc   = f"패닉셀 수급 ({turnover_today:.0f}억원). 바닥 신호 유력"
            vol_score  = 14 if turnover_today >= 100 else 8   # 대형주 패닉셀은 점수 가산
        elif capped_ratio >= 2.0 and price_chg > 0.01:
            vol_status = "red"
            vol_label  = f"거래량 {capped_ratio:.1f}배 + 상승 — 추격 ({turnover_today:.0f}억)"
            vol_desc   = "상승 동반 대량 거래 = 추격 위험"
            vol_score  = -8
        elif capped_ratio <= 0.4:
            vol_status = "yellow"
            vol_label  = f"거래량 {capped_ratio:.1f}배 — 무기력 ({turnover_today:.0f}억)"
            vol_desc   = "투항 후 무관심 구간"
            vol_score  = 3
        else:
            vol_status = "yellow"
            vol_label  = f"거래량 {capped_ratio:.1f}배 / {turnover_today:.0f}억"
            vol_desc   = "특이 신호 없음"
            vol_score  = 0

        results["volume"] = {
            "status": vol_status, "label": vol_label,
            "desc": vol_desc, "score": vol_score,
            "turnover": turnover_today
        }
    except Exception:
        results["volume"] = {"status": "yellow", "label": "거래량 — 계산 불가",
                             "desc": "데이터 부족", "score": 0}
        
# ── 4-1. OBV 다이버전스 (매집/분산 감지) ─────────────────────
    try:
        obv = (np.sign(close_series.diff()).fillna(0) * volume_series).cumsum()
        lookback = 20
        p_win, o_win = close_series.iloc[-lookback:], obv.iloc[-lookback:]

        p_rng = p_win.max() - p_win.min()
        o_rng = o_win.max() - o_win.min()
        p_pos = (p_win.iloc[-1] - p_win.min()) / p_rng * 100 if p_rng > 0 else 50
        o_pos = (o_win.iloc[-1] - o_win.min()) / o_rng * 100 if o_rng > 0 else 50

        if p_pos <= 15 and o_pos >= 45:
            obv_status, obv_label = "green", f"강세 다이버전스 (가격{p_pos:.0f}%/OBV{o_pos:.0f}%)"
            obv_desc, obv_score   = "가격 저점인데 거래량은 안 빠짐 = 매집 정황", 15
        elif p_pos >= 85 and o_pos <= 55:
            obv_status, obv_label = "red", f"약세 다이버전스 (가격{p_pos:.0f}%/OBV{o_pos:.0f}%)"
            obv_desc, obv_score   = "고점인데 거래량 뒷받침 약함 = 분산 정황", -8
        else:
            obv_status, obv_label = "yellow", f"다이버전스 없음 ({p_pos:.0f}%/{o_pos:.0f}%)"
            obv_desc, obv_score   = "가격·거래량 동행 중", 0

        results["obv"] = {"status": obv_status, "label": obv_label, "desc": obv_desc, "score": obv_score}
    except Exception:
        results["obv"] = {"status": "yellow", "label": "OBV — 계산 불가", "desc": "데이터 부족", "score": 0}
        
# ── 5. 외국인 순매수
    try:
        url_f  = f"https://finance.naver.com/item/frgn.naver?code={ticker_code}"
        hdrs_f = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": f"https://finance.naver.com/item/main.naver?code={ticker_code}"
        }
        resp_f = requests.get(url_f, headers=hdrs_f, timeout=6)
        content = resp_f.content
        html_f = content.decode("euc-kr", errors="replace") if b"euc-kr" in content[:500].lower() else content.decode("utf-8", errors="replace")
        soup_f = BeautifulSoup(html_f, "html.parser")

        rows_f = soup_f.select("table.type2 tr")
        net_values = []
        for row in rows_f:
            tds = row.select("td")
            if len(tds) < 8:          # 컬럼 8개 미만 행 스킵
                continue
            try:
                val_text = tds[6].get_text().strip().replace(",", "").replace("+", "")
                if not val_text or val_text == "-":
                    continue
                val = int(val_text)
                net_values.append(val)
            except (ValueError, IndexError):
                continue
            if len(net_values) >= 5:
                break

        if len(net_values) < 2:
            raise ValueError(f"파싱 실패: {len(net_values)}건")

        consec_sell = sum(1 for v in net_values[:3] if v < 0)
        consec_buy  = sum(1 for v in net_values[:3] if v > 0)
        recent_sum  = sum(net_values[:3]) // 100

        # 전환 감지: 직전 3일 매도 → 최근 1일 매수
        is_turning = (net_values[0] > 0 and net_values[1] < 0 and net_values[2] < 0)
        is_still_selling = consec_sell >= 3

        if is_turning:
            fg_status, fg_label = "green", f"외국인 매도→매수 전환 ({net_values[0]//100:+,}억)"
            fg_desc, fg_score   = "수급 전환 포착. 역발상 진입 트리거", 15
        elif consec_sell >= 3 and abs(net_values[0]) < abs(net_values[1]):
            # 매도하고 있지만 매도량 감소 중 = 이탈 둔화
            fg_status, fg_label = "yellow", f"외국인 매도 둔화 ({recent_sum:+,}억)"
            fg_desc, fg_score   = "이탈 속도 감소. 전환 대기 구간", 5
        elif is_still_selling:
            fg_status, fg_label = "red", f"외국인 연속 이탈 ({recent_sum:+,}억)"
            fg_desc, fg_score   = "수급 이탈 진행 중. 진입 대기", -8
        elif consec_buy >= 2:
            fg_status, fg_label = "yellow", f"외국인 순매수 중 ({recent_sum:+,}억)"
            fg_desc, fg_score   = "외국인 유입. 공포 구간 아님", -3
        else:
            fg_status, fg_label = "yellow", "외국인 혼조세"
            fg_desc, fg_score   = "방향성 없음", 0

        results["foreign"] = {
            "status": fg_status, "label": fg_label,
            "desc": fg_desc, "score": fg_score,
            "is_turning": is_turning,
            "is_still_selling": is_still_selling
        }

    except Exception as e:
        results["foreign"] = {"status": "yellow", "label": f"외국인 — {str(e)[:45]}", "desc": "잠시 후 재시도", "score": 0}

# ── 10. 공포-거래량 괴리 지수 ─────────────────────────────────
    try:
        if len(close_series) >= 6 and len(volume_series) >= 6:
            price_chg_5d = (float(close_series.iloc[-1]) - float(close_series.iloc[-6])) / float(close_series.iloc[-6])
            vol_chg_5d   = (float(volume_series.iloc[-1]) - float(volume_series.iloc[-6])) / float(volume_series.iloc[-6])

            if price_chg_5d < -0.03 and vol_chg_5d > 0.5:
                pvd_status, pvd_label = "green", f"패닉셀 감지 (가격↓{price_chg_5d*100:.1f}% / 거래량↑{vol_chg_5d*100:.0f}%)"
                pvd_desc, pvd_score   = "하락+거래량 폭발 = 투매 클라이맥스. 바닥 신호 최강", 15
            elif price_chg_5d < -0.03 and vol_chg_5d < -0.2:
                pvd_status, pvd_label = "yellow", f"무관심 하락 (가격↓{price_chg_5d*100:.1f}% / 거래량↓)"
                pvd_desc, pvd_score   = "하락+거래량 감소 = 아직 바닥 탐색 중. 대기 권고", 3
            elif price_chg_5d > 0.05 and vol_chg_5d > 0.5:
                pvd_status, pvd_label = "red", f"추격 위험 (가격↑{price_chg_5d*100:.1f}% / 거래량↑{vol_chg_5d*100:.0f}%)"
                pvd_desc, pvd_score   = "상승+거래량 폭발 = FOMO 추격 위험 구간", -5
            else:
                pvd_status, pvd_label = "yellow", f"괴리 미포착 (가격{price_chg_5d*100:+.1f}%)"
                pvd_desc, pvd_score   = "뚜렷한 패닉셀/추격 신호 없음", 0

            results["pvd"] = {"status": pvd_status, "label": pvd_label, "desc": pvd_desc, "score": pvd_score}
        else:
            raise ValueError("데이터 부족")
    except Exception:
        results["pvd"] = {"status": "yellow", "label": "괴리 지수 — 계산 불가", "desc": "데이터 부족", "score": 0}

# ── 11. 뉴스 공백 지수 ────────────────────────────────────────
    try:
        import urllib.parse
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

        if today_count == 0:
            nv_status, nv_label = "green", "뉴스 완전 공백 — 관심 소멸"
            nv_desc, nv_score   = "미디어 무관심 극대화. 역발상 저점 신호", 8
        elif today_ratio <= 0.15:
            nv_status, nv_label = "green", f"뉴스 희소 (당일 {today_count}건)"
            nv_desc, nv_score   = "언론 관심 낮음. 조용한 바닥 구간 가능", 4
        elif today_ratio >= 0.6:
            nv_status, nv_label = "red", f"뉴스 폭발 (당일 {today_count}건)"
            nv_desc, nv_score   = "미디어 과열 = 대중 관심 극대 = 고점 경계", -5
        else:
            nv_status, nv_label = "yellow", f"뉴스 보통 (당일 {today_count}건)"
            nv_desc, nv_score   = "정상 수준 언론 관심", 0

        results["news_vacuum"] = {"status": nv_status, "label": nv_label, "desc": nv_desc, "score": nv_score}
    except Exception:
        results["news_vacuum"] = {"status": "yellow", "label": "뉴스 지수 — 수집 불가", "desc": "잠시 후 재시도", "score": 0}



    # ── 최종 총점 (가중치 재조정)
    # 커뮤니티+뉴스: 25% / 가격(RSI+볼린저+52주): 35% / 수급(PVD+외국인+공매도): 40%
    price_keys_score  = sum(results.get(k, {}).get("score", 0) for k in ["rsi", "bb", "w52", "ichimoku"])
    supply_keys_score = sum(results.get(k, {}).get("score", 0) for k in ["volume", "foreign", "obv", "pvd"])
    news_score        = results.get("news_vacuum", {}).get("score", 0) 
    
        # 각 그룹 정규화 후 가중합
# calculate_objective_indicators 함수 마지막 총점 계산 교체
    price_normalized  = max(-30, min(40, price_keys_score))  * 0.35
    supply_normalized = max(-30, min(40, supply_keys_score)) * 0.40
    news_normalized   = max(-10, min(10, news_score))        * 0.25
    
    raw_obj_score = price_normalized + supply_normalized + news_normalized
    base_offset = 40 if is_kosdaq else 35
    objective_score = int(max(0, min(80, raw_obj_score * 0.7 + base_offset)))
    return results, objective_score

def calculate_fomo_index(ticker_code):
    try:
        url = f"https://finance.naver.com/item/frgn.naver?code={ticker_code}"
        hdrs = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": f"https://finance.naver.com/item/main.naver?code={ticker_code}"
        }
        resp = requests.get(url, headers=hdrs, timeout=6)
        html = resp.content.decode("euc-kr", errors="replace") if b"euc-kr" in resp.content[:500].lower() else resp.content.decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")

        # 개인 순매수 컬럼 (frgn 페이지 테이블: 날짜/외국인/기관/개인 순)
        rows = soup.select("table.type2 tr")
        indiv_values = []
        for row in rows:
            tds = row.select("td")
            if len(tds) < 6:
                continue
            try:
                val = int(tds[5].get_text().strip().replace(",","").replace("+",""))
                indiv_values.append(val)
            except Exception:
                continue
            if len(indiv_values) >= 10:
                break

        if len(indiv_values) < 3:
            raise ValueError("개인 데이터 부족")

        recent_3d = sum(indiv_values[:3])
        hist_mean = sum(abs(v) for v in indiv_values) / len(indiv_values)
        fomo_ratio = recent_3d / hist_mean if hist_mean > 0 else 0

        if fomo_ratio >= 2.0:
            score, label = 90, f"개미 추격매수 과열 ({fomo_ratio:.1f}배)"
            desc, color  = "개인 순매수 급증 = 상투 위험 구간", "#dc2626"
        elif fomo_ratio >= 1.0:
            score, label = 60, f"개미 관심 증가 ({fomo_ratio:.1f}배)"
            desc, color  = "개인 매수 활발. 주의 구간", "#ca8a04"
        elif fomo_ratio <= -1.5:
            score, label = 15, f"개미 이탈 중 ({fomo_ratio:.1f}배)"
            desc, color  = "개인 순매도 = 공포 극대화. 역발상 유리", "#22c55e"
        else:
            score, label = 40, "개미 중립"
            desc, color  = "뚜렷한 쏠림 없음", "#475569"

        return {"score": score, "label": label, "desc": desc, "color": color}
    except Exception as e:
        return {"score": 50, "label": f"FOMO — {str(e)[:30]}", "desc": "수집 불가", "color": "#475569"}
 
st.markdown("### 🔍 종목 탐색기")

def _render_landing():
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px 40px 20px;">
      <div style="font-size:56px; margin-bottom:16px;">🤖</div>
      <h1 style="font-size:32px; font-weight:800; color:#f1f5f9; margin-bottom:8px;">
        개미반대로
      </h1>
      <p style="font-size:16px; color:#94a3b8; margin-bottom:4px;">
        군중이 공포에 떨 때, 숫자는 기회를 말한다
      </p>
      <p style="font-size:13px; color:#475569; margin-bottom:40px;">
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
# Smart Search Box with Autocomplete
# 교체
selected_item = st_searchbox(
    search_companies,
    default=st.session_state.get("last_selected", None),
    key="stock_searchbox",
    placeholder="🔍 종목명 또는 종목코드 입력 (예: 삼성전자, 005930)"
)

# 유효한 선택이면 저장, 아니면 마지막 저장값 사용
if selected_item and "(" in selected_item:
    st.session_state["last_selected"] = selected_item
    st.session_state["dashboard_ready"] = True
elif st.session_state.get("dashboard_ready"):
    selected_item = st.session_state["last_selected"]
else:
    _render_landing()
    st.stop()
 
# Parse Ticker and Name
selected_company = selected_item.split(" (")[0]
ticker_input = selected_item.split(" (")[1].replace(")", "").strip()
 
st.success(f"✅ **{selected_company}**({ticker_input}) 대시보드를 안정적으로 로드했습니다.")
st.markdown("---")
 
# Download Price Data (KOSPI vs KOSDAQ Suffix Handling)
@st.cache_data(ttl=60 * 10, show_spinner=False)
def load_price_data(ticker_code: str):
    result_data = pd.DataFrame()
    result_suffix = None

    for suffix in [".KS", ".KQ"]:
        try:
            data = yf.download(
                f"{ticker_code}{suffix}",
                period="1y",
                interval="1d",
                progress=False,
                auto_adjust=True,
            )
            if not data.empty:
                # MultiIndex 컬럼 평탄화 (yfinance 최신 버전 대응)
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                result_data = data
                result_suffix = suffix
                break
        except Exception:
            continue

    # 당일 데이터 누락 시 fdr로 보완
    if not result_data.empty:
            last_date = result_data.index[-1].date()
            today = pd.Timestamp.now().date()
            if last_date < today:
                try:
                    fdr_supplement = fdr.DataReader(
                        ticker_code,
                        start=(pd.Timestamp.now() - pd.Timedelta(days=365)).strftime("%Y-%m-%d")
                    )
                    if not fdr_supplement.empty:
                        # 인덱스 timezone 제거하여 비교 정합성 확보
                        if isinstance(result_data.columns, pd.MultiIndex):
                            result_data.columns = result_data.columns.get_level_values(0)
                        result_data.index = pd.to_datetime(result_data.index).tz_localize(None)

                        result_data.index = pd.to_datetime(result_data.index).tz_localize(None)
                        fdr_supplement.index = pd.to_datetime(fdr_supplement.index).tz_localize(None)

                        fdr_supplement = fdr_supplement[~fdr_supplement.index.isin(result_data.index)]
                        # 컬럼 구조 일치시키기 (yfinance: Open/High/Low/Close/Volume)
                        needed_cols = ["Open", "High", "Low", "Close", "Volume"]
                        common_cols = [c for c in needed_cols if c in result_data.columns and c in fdr_supplement.columns]

                        if not fdr_supplement.empty and len(common_cols) >= 4:
                            fdr_supplement = fdr_supplement[common_cols]
                            result_data = result_data[common_cols]
                            result_data = pd.concat([result_data, fdr_supplement])
                            result_data = result_data.sort_index()
                except Exception:
                    pass

    # 최종 안전장치: NaN 행 제거
    if not result_data.empty:
        if isinstance(result_data.columns, pd.MultiIndex):
            result_data.columns = result_data.columns.get_level_values(0)
        if "Close" in result_data.columns:
            result_data = result_data.dropna(subset=["Close"])
    else:
        # yfinance 완전 실패 시 fdr 단독 사용
        try:
            fdr_data = fdr.DataReader(ticker_code, start=(pd.Timestamp.now() - pd.Timedelta(days=365)))
            if not fdr_data.empty:
                result_data = fdr_data
                result_suffix = ".KQ"  # fdr만 성공한 경우 임시값, 아래 로직에서 보정 필요
        except Exception:
            pass

    return result_data, result_suffix
# 교체
df, market_suffix = load_price_data(ticker_input)
is_kosdaq = (market_suffix == ".KQ")
 
try:
    if df.empty:
        raise ValueError("데이터를 찾을 수 없습니다.")
        
    df = df.reset_index()
    dates_cleaned = df['Date'].squeeze()
    close_cleaned = df['Close'].squeeze()
    dates_korean = pd.to_datetime(dates_cleaned).dt.strftime('%Y.%m.%d')
    
    current_price = int(close_cleaned.iloc[-1])
    prev_price = int(close_cleaned.iloc[-2])
    change_pct = ((current_price - prev_price) / prev_price) * 100
    
    # Load Real Naver Posts (Sorted by Likes/Views) and DC Simulator
    naver_posts = get_naver_discussion_by_likes(ticker_input)

    high_cleaned = df['High'].squeeze() if 'High' in df.columns else None
    low_cleaned  = df['Low'].squeeze()  if 'Low'  in df.columns else None

    community_raw, ai_reason, community_score, volatility_warning = analyze_combined_sentiment(
        naver_posts,
        close_series=close_cleaned,
        high_series=high_cleaned,
        low_series=low_cleaned
    )

    volume_series = df['Volume'].squeeze() if 'Volume' in df.columns else pd.Series(dtype=float)
    obj_indicators, objective_score = calculate_objective_indicators(
    close_cleaned, volume_series, ticker_input, high_cleaned, low_cleaned, is_kosdaq=is_kosdaq
    )
    fomo_data = calculate_fomo_index(ticker_input)

    rsi_val       = obj_indicators.get("rsi",     {}).get("value", 50) or 50
    w52_score     = obj_indicators.get("w52",     {}).get("score", 0)
    vol_score     = obj_indicators.get("volume",  {}).get("score", 0)
    pvd_score     = obj_indicators.get("pvd",     {}).get("score", 0)
    bb_score      = obj_indicators.get("bb",      {}).get("score", 0)
    obv_score     = obj_indicators.get("obv", {}).get("score", 0)
    foreign_score = obj_indicators.get("foreign", {}).get("score", 0)
    fomo_score    = fomo_data["score"]

    is_near_high   = w52_score <= -8
    is_near_low    = w52_score >= 10
    is_fomo_hot    = fomo_score >= 70
    is_panic_sell  = pvd_score >= 12
    is_rsi_hot     = rsi_val >= 65
    is_rsi_cold    = rsi_val <= 35
    is_supply_fear = foreign_score >= 8
    
    drawdown_val     = obj_indicators.get("drawdown", {}).get("value", 0)
    is_high_drawdown = drawdown_val >= 30

    # 변경 후: objective_score를 base의 앵커로 활용
    # objective_score 범위 0~80 → 비명 지수 스케일(0~100)로 선형 변환 후 조건 보정값 가산
    obj_anchored = int(objective_score * (100 / 80))  # 0~100 스케일 정규화

    # 조건 분기는 보정값(delta)으로만 사용
    if   is_near_high and is_fomo_hot and is_rsi_hot:       base = 15
    elif is_near_high and is_fomo_hot:                      base = 22
    elif is_near_high and is_rsi_hot:                       base = 28
    elif is_near_high:                                      base = 35
    elif is_near_low and is_panic_sell and is_rsi_cold:     base = 88
    elif is_near_low and is_panic_sell:                     base = 78
    elif is_near_low and is_rsi_cold:                       base = 72
    elif is_near_low:                                       base = 63
    elif is_high_drawdown and is_panic_sell and is_rsi_cold: base = 75
    elif is_high_drawdown and is_rsi_cold:                  base = 65
    elif is_high_drawdown and is_panic_sell:                base = 68
    elif is_high_drawdown and bb_score >= 8:                base = 60
    elif is_high_drawdown:                                  base = 55
    elif is_panic_sell and is_rsi_cold:                     base = 70
    elif is_rsi_cold and bb_score >= 8:                     base = 65
    elif is_rsi_hot  and is_fomo_hot:                       base = 25
    elif is_rsi_hot:                                        base = 38
    else:                                                   base = 50

    adj = 0
    if is_supply_fear:      adj += 8
    if foreign_score >= 10: adj += 4
    if vol_score     >= 10: adj += 4
    if obv_score     >= 12: adj += 3
    if is_fomo_hot:         adj -= 7
    if community_raw >= 65: adj += 4
    if community_raw <= 35: adj -= 4
    if is_high_drawdown: adj += 5
    adj = max(-10, min(10, adj))

    kosdaq_adj = 3 if is_kosdaq else 0
    final_scream_score = int(max(5, min(95, base + adj + kosdaq_adj)))

    # 임계값 구간 판정 텍스트 (게이지 아래 표시용)
    if final_scream_score >= 85:
        scream_tier = ("🔥 극단 공포", "#dc2626", "역발상 매수 최적 구간 — 군중 공포 극대화")
    elif final_scream_score >= 70:
        scream_tier = ("😱 공포 구간", "#ea580c", "분할매수 진입 고려 — 공포 우세")
    elif final_scream_score >= 55:
        scream_tier = ("⚡ 공포 진입", "#ca8a04", "관심 구간 — 신호 모니터링")
    elif final_scream_score >= 35:
        scream_tier = ("😐 중립", "#475569", "군중심리 과열 없음 — 대기")
    else:
        scream_tier = ("🚀 탐욕 과열", "#16a34a", "역발상 매도 고려 — FOMO 극대화")
    
    # Display Layout (Ratio 6 : 4 — 오른쪽 사이드에 지표 카드가 많아 여유 필요)
    col_main, col_side = st.columns([6, 4])
    
    with col_main:
        st.subheader(f"📊 개미 환불선 스캐너 ({selected_company})")
 
        # ── 최고점 / 최저점 탐색 ──────────────────────────────
        max_idx = close_cleaned.idxmax()
        min_idx = close_cleaned.idxmin()
        max_price = int(close_cleaned.loc[max_idx])
        min_price = int(close_cleaned.loc[min_idx])
        max_date = dates_korean.loc[max_idx]
        min_date = dates_korean.loc[min_idx]
 
        # 차트에 사용할 데이터를 JS로 넘기기 위해 JSON 직렬화
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
        
        #개미환불선
        def calc_vwap_refund_line(df_raw):
            """
            30일 VWAP = Σ(전형가 × 거래량) / Σ(거래량)
            전형가(Typical Price) = (고가 + 저가 + 종가) / 3
            거래량 데이터 없을 시 단순 30일 MA 폴백
            """
            try:
                high = df_raw['High'].squeeze()
                low  = df_raw['Low'].squeeze()
                close = df_raw['Close'].squeeze()
                vol  = df_raw['Volume'].squeeze()
        
                typical = (high + low + close) / 3
                vwap = (typical * vol).sum() / vol.sum()
                return int(vwap)
            except Exception:
                return int(df_raw['Close'].squeeze().mean())
        #피보나치    
        def calc_fibonacci_nearest(close_series):
            high, low = float(close_series.max()), float(close_series.min())
            diff = high - low
            if diff <= 0:
                return None
            levels = {0.382: high - diff * 0.382, 0.5: high - diff * 0.5, 0.618: high - diff * 0.618}
            current = float(close_series.iloc[-1])
            nearest_pct, nearest_price = min(levels.items(), key=lambda kv: abs(current - kv[1]))
            status = "이탈" if current < nearest_price else "지지"
            return nearest_pct, nearest_price, status    

        ant_refund_line = calc_vwap_refund_line(df)

        
        up_down_emoji = "🔺" if change_pct >= 0 else "🔻"
        vwap_status = "🔴 개미 대부분 손실 구간" if current_price < ant_refund_line else "🟢 개미 대부분 수익 구간"
        vwap_label  = f"개미 평단 추정선: **{ant_refund_line:,}원** {vwap_status}"

        st.info(f"현재 주가: **{current_price:,}원** ({up_down_emoji} {change_pct:+.2f}%) | {vwap_label}")
        #피보나치
        fib = calc_fibonacci_nearest(close_cleaned)
        if fib:
            pct, price, status = fib
            gap_pct = (current_price - price) / price * 100
            fib_color = "#22c55e" if status == "지지" else "#ef4444"
            fib_icon  = "🛡️" if status == "지지" else "⚠️"
            fib_msg = "현재가가 이 라인 위에 있어 '지지선' 역할을 하고 있어요." if status == "지지" \
                    else "현재가가 이 라인 아래로 내려가 '저항선'으로 바뀐 상태예요."
            st.markdown(f"""
            <div style="background:#0f172a; border:1px solid {fib_color}55; border-radius:8px;
                padding:10px 14px; margin:6px 0 10px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:12.5px; color:#e2e8f0; font-weight:700;">{fib_icon} 피보나치 되돌림 {pct*100:.1f}%</span>
                <span style="font-size:11.5px; color:{fib_color}; font-weight:700;">{status} ({gap_pct:+.1f}%)</span>
            </div>
            <div style="font-size:11px; color:#94a3b8; margin-top:4px;">
                기준가 <b style="color:#f1f5f9;">{price:,.0f}원</b> — 52주 고점·저점 사이에서 되돌림이 자주 나오는 가격대예요. {fib_msg}
            </div>
            </div>
            """, unsafe_allow_html=True)
        
        #변동성 경고 표시
        if volatility_warning:
            st.warning(volatility_warning)
        #커뮤니티 탭
        st.markdown("#### 🔥 실시간 주주 비명소리")
        tab1, = st.tabs(["📌 네이버 인기글 (실시간 공감순)"])  # DC탭 삭제
    
        with tab1:
            cols_post = st.columns(2)  # 2열 그리드로 가독성 향상
            for idx, post in enumerate(naver_posts[:8], 0):
                likes = post['likes']
                badge_color = "#16a34a" if likes >= 20 else "#ca8a04" if likes >= 5 else "#475569"
                with cols_post[idx % 2]:
                    st.markdown(
                        f"""<div style="background:#0f172a; border-radius:8px; padding:9px 11px;
                            margin-bottom:8px; border-left:3px solid {badge_color};">
                        <div style="font-size:12px; color:#e2e8f0; line-height:1.4; margin-bottom:4px;">{post['title']}</div>
                        <div style="font-size:10.5px; color:#64748b;">👍 {post['likes']} &nbsp;·&nbsp; 👀 {post['views']}</div>
                        </div>""",
                        unsafe_allow_html=True
                    )
        
 

# 1232줄 위치에 함수 정의 삽입
    def get_entry_signal(obj_indicators, final_scream_score, fomo_score):
        foreign = obj_indicators.get("foreign", {})
        obv     = obj_indicators.get("obv",     {})
        pvd     = obj_indicators.get("pvd",     {})
        rsi     = obj_indicators.get("rsi",     {})

        is_fear_zone    = final_scream_score >= 60
        is_fg_turning   = foreign.get("is_turning", False)
        is_fg_selling   = foreign.get("is_still_selling", False)
        is_obv_bullish  = obv.get("status") == "green"
        is_obv_bearish  = obv.get("status") == "red"
        is_panic_done   = pvd.get("score", 0) >= 12
        is_rsi_cold     = (rsi.get("value") or 50) <= 35

        if is_fear_zone and is_fg_turning and is_obv_bullish:
            return {"level": "🟢 진입 적극 고려", "color": "#22c55e",
                    "desc": "공포 + 외국인 전환 + OBV 매집 동시 포착. 최적 타점",
                    "action": "분할매수 1차 진입"}
        elif is_fear_zone and (is_fg_turning or is_obv_bullish) and is_panic_done:
            return {"level": "🟡 조건부 진입", "color": "#eab308",
                    "desc": "공포 + 수급 일부 전환. 나머지 신호 대기하며 소량 선진입",
                    "action": "소량 선매수 / 나머지 신호 대기"}
        elif is_fear_zone and is_fg_selling and is_obv_bearish:
            return {"level": "🔴 진입 보류", "color": "#ef4444",
                    "desc": "공포 구간이나 외국인 이탈·OBV 분산 진행 중",
                    "action": "예수금 보유. 전환 신호 재확인"}
        elif not is_fear_zone:
            return {"level": "⚫ 관망", "color": "#475569",
                    "desc": "공포 구간 미진입. 역발상 타점 아님",
                    "action": "대기"}
        else:
            return {"level": "🟡 대기", "color": "#ca8a04",
                    "desc": "공포 감지. 수급 전환 신호 미확인",
                    "action": "알림 설정 후 대기"}

    # 1233줄: with col_side: ← 기존 코드 이어짐
    with col_side:
        st.subheader("😱 실시간 공포 스탯")
        
        entry = get_entry_signal(obj_indicators, final_scream_score, fomo_score)
        st.markdown(
            f"""<div style="background:#0f172a; border:2px solid {entry['color']}55;
                border-radius:10px; padding:14px 16px; margin:0 0 14px 0;">
            <div style="font-size:15px; font-weight:700; color:{entry['color']};
                margin-bottom:4px;">{entry['level']}</div>
            <div style="font-size:11.5px; color:#94a3b8; margin-bottom:6px;">{entry['desc']}</div>
            <div style="background:{entry['color']}22; border-radius:6px; padding:6px 10px;
                font-size:12px; color:{entry['color']}; font-weight:600;">
                → {entry['action']}
            </div>
            </div>""",
            unsafe_allow_html=True
        )
 
        # ── 통합 비명 지수 게이지 ─────────────────────────────────────
        # 점수별 게이지 색상
        if final_scream_score >= 85:
            gauge_color, number_color = "#dc2626", "#ff4444"
        elif final_scream_score >= 70:
            gauge_color, number_color = "#ea580c", "#fb923c"
        elif final_scream_score >= 55:
            gauge_color, number_color = "#ca8a04", "#fbbf24"
        elif final_scream_score >= 35:
            gauge_color, number_color = "#475569", "#94a3b8"
        else:
            gauge_color, number_color = "#16a34a", "#4ade80"

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=final_scream_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "통합 비명 지수", 'font': {'size': 14, 'color': '#e2e8f0'}},
            number={'font': {'size': 48, 'color': number_color}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#475569",
                        'tickfont': {'color': '#94a3b8'}},
                'bar': {'color': gauge_color},
                'bgcolor': "#0f172a",
                'borderwidth': 1,
                'bordercolor': "#1e293b",
                'steps': [
                    {'range': [0,  35], 'color': '#052e16'},   # 탐욕 — 다크그린
                    {'range': [35, 55], 'color': '#1e293b'},   # 중립 — 다크슬레이트
                    {'range': [55, 70], 'color': '#2d1f00'},   # 공포진입 — 다크옐로
                    {'range': [70, 85], 'color': '#2d0f00'},   # 공포 — 다크오렌지
                    {'range': [85,100], 'color': '#1f0000'},   # 극단공포 — 다크레드
                ],
                'threshold': {'line': {'color': gauge_color, 'width': 3},
                            'thickness': 0.75, 'value': final_scream_score}
            }
        ))
        fig_gauge.update_layout(
            height=210,
            margin=dict(l=15, r=15, t=35, b=5),
            font={'family': "Malgun Gothic"},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        tier_label, tier_color, tier_desc = scream_tier
        st.markdown(
            f"""<div style="text-align:center; background:#0f172a; border:1px solid {tier_color}33;
                border-radius:8px; padding:8px; margin:-4px 0 10px 0;">
            <span style="color:{tier_color}; font-size:15px; font-weight:700;">{tier_label}</span><br>
            <span style="color:#94a3b8; font-size:10.5px;">{tier_desc}</span>
            </div>""",
            unsafe_allow_html=True
        )
        

        # 커뮤니티 / 객관 점수 한 줄 분리
        # 교체
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            st.metric("💬 커뮤니티", f"{int(community_raw)}점", help="네이버 여론 (25%)")
        with g_col2:
            st.metric("📐 객관지표", f"{int(objective_score)}점", help="RSI·수급 등 (75%)")
        
        # ── 종합 판정 카드 (게이지 바로 아래) ────────────────────────
        indicator_meta = [
            ("rsi",      "📈 RSI (14일)",      "가격"),
            ("bb",       "〰️ 볼린저 밴드",     "가격"),
            ("w52",      "📉 52주 신저가",     "가격"),
            ("drawdown", "📉 고점낙폭", "가격"),  # 신규
            ("volume",   "🔊 거래량",          "수급"),
            ("foreign",  "🌍 외국인",          "수급"),
            ("obv", "📊 OBV 다이버전스", "수급")
        ]
        green_count = sum(1 for k,_,_ in indicator_meta if obj_indicators.get(k,{}).get("status") == "green")
        total_count = len(indicator_meta)
 
        if green_count >= 4:
            vd_bg, vd_border, vd_icon = "#0d2b1a", "#22c55e", "🔥"
            vd_text = f"신호 {green_count}/{total_count}개 포착 — 강력 역발상 매수 구간"
        elif green_count >= 2:
            vd_bg, vd_border, vd_icon = "#2b2200", "#eab308", "⚡️"
            vd_text = f"신호 {green_count}/{total_count}개 포착 — 보수적 분할 접근"
        else:
            vd_bg, vd_border, vd_icon = "#1e293b", "#475569", "💤"
            vd_text = f"신호 {green_count}/{total_count}개 — 관망 및 예수금 대기"
 
        st.markdown(
            f"""<div style="background:{vd_bg}; border:2px solid {vd_border}; border-radius:10px;
                 padding:12px 14px; margin:6px 0 14px 0; display:flex; align-items:center; gap:10px;">
              <span style="font-size:20px;">{vd_icon}</span>
              <span style="font-size:12.5px; color:#f1f5f9; font-weight:600; line-height:1.4;">{vd_text}</span>
            </div>""",
            unsafe_allow_html=True
        )

        attention_score = fomo_data["score"]
        # 기존 관심도 패널 st.markdown 교체
        bar_width = min(100, int(fomo_data["score"]))
        bar_color = fomo_data["color"]
        st.markdown(
            f"""<div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px;
                padding:12px 14px; margin:0 0 12px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-size:12px; font-weight:700; color:#e2e8f0;">🎯 개미 관심도 지수</span>
                <span style="font-size:20px; font-weight:800; color:{bar_color};">{int(fomo_data['score'])}점</span>
            </div>
            <div style="font-size:11px; color:{bar_color}; font-weight:600; margin-bottom:6px;">{fomo_data['label']}</div>
            <div style="background:#1e293b; border-radius:6px; height:8px; margin-bottom:6px;">
                <div style="background:{bar_color}; width:{bar_width}%; height:8px; border-radius:6px;"></div>
            </div>
            <div style="font-size:10.5px; color:#94a3b8;">{fomo_data['desc']}</div>
            <div style="font-size:10px; color:#475569; margin-top:4px;">
                📌 관심도 높음+공포 높음 = 반등 강도 ↑ &nbsp;|&nbsp; 관심도 낮음+공포 높음 = 바닥 탐색 중
            </div>
            </div>""",
            unsafe_allow_html=True
        )
 
        # ── 5개 객관 지표 신호등 카드 ─────────────────────────────────
        STATUS_STYLE = {
            "green":  {"bg": "#0d2b1a", "border": "#22c55e", "badge_bg": "#16a34a", "badge_text": "✅ 신호 포착"},
            "yellow": {"bg": "#1c1a00", "border": "#eab308", "badge_bg": "#854d0e", "badge_text": "⚠️ 중립"},
            "red":    {"bg": "#1a0606", "border": "#ef4444", "badge_bg": "#991b1b", "badge_text": "❌ 미포착"},
        }
 
        # 가격 기반 / 수급 기반 그룹 헤더로 구분
        price_keys = [
            ("rsi",      "📈 RSI (14일)"),
            ("bb",       "〰️ 볼린저 밴드"),
            ("w52",      "📉 52주 신저가"),
            ("drawdown", "📉 고점 대비 낙폭"),  # 신규
            ("ichimoku", "☁️ 일목균형표"),
        ]
        supply_keys = [
            ("volume",      "🔊 거래량 폭발"),
            ("pvd",         "💥 공포-거래량 괴리"),
            ("foreign",     "🌍 외국인 동향"),
            ("obv", "📊 OBV 다이버전스")
        ]
 
        st.markdown("<p style='font-size:11px; color:#64748b; font-weight:700; margin:0 0 4px 2px; letter-spacing:0.5px;'>▸ 가격 기반</p>", unsafe_allow_html=True)
        for key, title in price_keys:
            ind = obj_indicators.get(key, {})
            sty = STATUS_STYLE[ind.get("status", "yellow")]
            st.markdown(
                f"""<div style="background:{sty['bg']}; border:1px solid {sty['border']};
                     border-radius:8px; padding:10px 12px; margin-bottom:6px;">
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                    <span style="font-size:12px; font-weight:700; color:#e2e8f0;">{title}</span>
                    <span style="background:{sty['badge_bg']}; color:white; font-size:10px;
                           padding:1px 7px; border-radius:20px; font-weight:600; white-space:nowrap;">{sty['badge_text']}</span>
                  </div>
                  <div style="font-size:12px; color:#f1f5f9; font-weight:600; margin-bottom:1px;">{ind.get('label','—')}</div>
                  <div style="font-size:10.5px; color:#94a3b8;">{ind.get('desc','—')}</div>
                </div>""",
                unsafe_allow_html=True
            )
 
        st.markdown("<p style='font-size:11px; color:#64748b; font-weight:700; margin:8px 0 4px 2px; letter-spacing:0.5px;'>▸ 수급 기반</p>", unsafe_allow_html=True)
        for key, title in supply_keys:
            ind = obj_indicators.get(key, {})
            sty = STATUS_STYLE[ind.get("status", "yellow")]
            st.markdown(
                f"""<div style="background:{sty['bg']}; border:1px solid {sty['border']};
                     border-radius:8px; padding:10px 12px; margin-bottom:6px;">
                  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
                    <span style="font-size:12px; font-weight:700; color:#e2e8f0;">{title}</span>
                    <span style="background:{sty['badge_bg']}; color:white; font-size:10px;
                           padding:1px 7px; border-radius:20px; font-weight:600; white-space:nowrap;">{sty['badge_text']}</span>
                  </div>
                  <div style="font-size:12px; color:#f1f5f9; font-weight:600; margin-bottom:1px;">{ind.get('label','—')}</div>
                  <div style="font-size:10.5px; color:#94a3b8;">{ind.get('desc','—')}</div>
                </div>""",
                unsafe_allow_html=True
            )
 
        st.markdown("---") 
except Exception as e:
    st.error(f"⚠️ 대시보드 로드 중 치명적인 문제가 발생했습니다. (에러: {e})")
    st.exception(e)