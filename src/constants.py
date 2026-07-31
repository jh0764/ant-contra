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

THEME = {
    "bg": "#F4F6FB", 
    "surface": "#FFFFFF", 
    "border": "#E2E8F0",
    "text_main": "#1A1D29", 
    "text_sub": "#6B7280",
}
PRICE_COLOR = {"up": "#f04452", "down": "#3182f6"}

TICKER_BADGE_COLORS = ["#f04452", "#3182f6", "#16a34a", "#eab308",
                        "#8b5cf6", "#ec4899", "#0891b2", "#f97316"]

STATUS_STYLE = {
    "green":  {"bg": "#DCFCE7", "border": "#16A34A", "badge_bg": "#16A34A", "badge_text": "포착",   "badge_color": "#FFFFFF"},
    "yellow": {"bg": "#FEF3C7", "border": "#CA8A04", "badge_bg": "#CA8A04", "badge_text": "중립",   "badge_color": "#FFFFFF"},
    "red":    {"bg": "#FEE2E2", "border": "#DC2626", "badge_bg": "#DC2626", "badge_text": "미포착", "badge_color": "#FFFFFF"},
}

ACCENT = "#FF7A2F"
SPACING = "10px"

# ── 지표 임계값 ──────────────────────────────────────────
RSI_OVERSOLD = 30
RSI_WEAK_RECOVERY = 45
RSI_OVERBOUGHT = 70

BB_LOWER_NEAR_PCT = 25
BB_UPPER_NEAR_PCT = 80

W52_LOW_NEAR_PCT = 5
W52_HIGH_NEAR_PCT = 3
W52_LOW_ZONE_PCT = 15

DRAWDOWN_DEEP = 40
DRAWDOWN_SIGNIFICANT = 25
DRAWDOWN_MODERATE = 15
DRAWDOWN_NEAR_HIGH = 5

VOL_SURGE_RATIO = 2.0
VOL_DEAD_RATIO = 0.4
VOL_MICRO_CAP_THRESHOLD_EOK = 10  # 억원

FOMO_HOT_THRESHOLD = 70
FOMO_COLD_THRESHOLD = -1.5

# ── 최종 공포지수 산출(scoring.py) 임계값 ──────────────────
SCORE_NEAR_HIGH_W52 = -8
SCORE_NEAR_LOW_W52 = 10
SCORE_RSI_HOT = 65
SCORE_RSI_COLD = 35
SCORE_PANIC_SELL_PVD = 12
SCORE_SUPPLY_FEAR_FOREIGN = 8
SCORE_HIGH_DRAWDOWN = 30
SCORE_FOREIGN_STRONG = 10
SCORE_VOL_STRONG = 10
SCORE_OBV_STRONG = 12
SCORE_COMMUNITY_HIGH = 65
SCORE_COMMUNITY_LOW = 35
SCORE_ADJ_MIN, SCORE_ADJ_MAX = -10, 10
SCORE_KOSDAQ_ADJ = 3
SCORE_FINAL_MIN, SCORE_FINAL_MAX = 5, 95