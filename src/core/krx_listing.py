import pandas as pd
import streamlit as st
import FinanceDataReader as fdr



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

# Company Search Function (전체 상장 종목 대상 부분일치 검색, 종목명/종목코드 모두 지원)
def search_companies(search_term, listing_df):
    if not search_term or len(search_term) < 1:
        return []
 
    term = search_term.strip().lower()
 
    if listing_df.empty:
        return []
 
    # 종목명에 검색어가 포함되거나, 종목코드가 검색어로 시작하는 경우 모두 매칭
    name_match = listing_df["Name"].str.lower().str.contains(term, na=False, regex=False)
    code_match = listing_df["Code"].str.startswith(term, na=False)
    matched = listing_df[name_match | code_match]
 
    # 검색어로 시작하는 종목명을 우선순위로 정렬 (예: "삼성" 검색 시 "삼성전자"가 상단에)
    starts_with = matched["Name"].str.lower().str.startswith(term)
    matched = pd.concat([matched[starts_with], matched[~starts_with]])
 
    matched = matched.head(30)  # 너무 많으면 드롭다운이 무거워지므로 상위 30개로 제한
    return [f"{row['Name']} ({row['Code']})" for _, row in matched.iterrows()]
 