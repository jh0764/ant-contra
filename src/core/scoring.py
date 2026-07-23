from core.naver_scraper import _fetch_frgn_rows
from constants import (
    FOMO_HOT_THRESHOLD, SCORE_NEAR_HIGH_W52, SCORE_NEAR_LOW_W52,
    SCORE_RSI_HOT, SCORE_RSI_COLD, SCORE_PANIC_SELL_PVD,
    SCORE_SUPPLY_FEAR_FOREIGN, SCORE_HIGH_DRAWDOWN,
    SCORE_FOREIGN_STRONG, SCORE_VOL_STRONG, SCORE_OBV_STRONG,
    SCORE_COMMUNITY_HIGH, SCORE_COMMUNITY_LOW,
    SCORE_ADJ_MIN, SCORE_ADJ_MAX, SCORE_KOSDAQ_ADJ,
    SCORE_FINAL_MIN, SCORE_FINAL_MAX,
)

def calculate_fomo_index(ticker_code):
    try:
        tds_rows = _fetch_frgn_rows(ticker_code)
        indiv_values = []
        for tds in tds_rows:
            try:
                val = int(tds[5].replace(",", "").replace("+", ""))
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

def _extract_score_flags(obj_indicators, fomo_score):
    rsi_val       = obj_indicators.get("rsi",     {}).get("value", 50) or 50
    w52_score     = obj_indicators.get("w52",     {}).get("score", 0)
    vol_score     = obj_indicators.get("volume",  {}).get("score", 0)
    pvd_score     = obj_indicators.get("pvd",     {}).get("score", 0)
    bb_score      = obj_indicators.get("bb",      {}).get("score", 0)
    obv_score     = obj_indicators.get("obv", {}).get("score", 0)
    foreign_score = obj_indicators.get("foreign", {}).get("score", 0)
    drawdown_val  = obj_indicators.get("drawdown", {}).get("value", 0)

    return {
        "vol_score": vol_score, "bb_score": bb_score, "obv_score": obv_score,
        "foreign_score": foreign_score,
        "is_near_high":   w52_score <= SCORE_NEAR_HIGH_W52,
        "is_near_low":    w52_score >= SCORE_NEAR_LOW_W52,
        "is_fomo_hot":    fomo_score >= FOMO_HOT_THRESHOLD,
        "is_panic_sell":  pvd_score >= SCORE_PANIC_SELL_PVD,
        "is_rsi_hot":     rsi_val >= SCORE_RSI_HOT,
        "is_rsi_cold":    rsi_val <= SCORE_RSI_COLD,
        "is_supply_fear": foreign_score >= SCORE_SUPPLY_FEAR_FOREIGN,
        "is_high_drawdown": drawdown_val >= SCORE_HIGH_DRAWDOWN,
    }


def _determine_base_score(f):
    is_near_high, is_near_low = f["is_near_high"], f["is_near_low"]
    is_fomo_hot, is_panic_sell = f["is_fomo_hot"], f["is_panic_sell"]
    is_rsi_hot, is_rsi_cold = f["is_rsi_hot"], f["is_rsi_cold"]
    is_high_drawdown, bb_score = f["is_high_drawdown"], f["bb_score"]

    if   is_near_high and is_fomo_hot and is_rsi_hot:       return 15
    elif is_near_high and is_fomo_hot:                      return 22
    elif is_near_high and is_rsi_hot:                       return 28
    elif is_near_high:                                      return 35
    elif is_near_low and is_panic_sell and is_rsi_cold:     return 88
    elif is_near_low and is_panic_sell:                     return 78
    elif is_near_low and is_rsi_cold:                       return 72
    elif is_near_low:                                       return 63
    elif is_high_drawdown and is_panic_sell and is_rsi_cold: return 75
    elif is_high_drawdown and is_rsi_cold:                  return 65
    elif is_high_drawdown and is_panic_sell:                return 68
    elif is_high_drawdown and bb_score >= 8:                return 60
    elif is_high_drawdown:                                  return 55
    elif is_panic_sell and is_rsi_cold:                     return 70
    elif is_rsi_cold and bb_score >= 8:                     return 65
    elif is_rsi_hot  and is_fomo_hot:                       return 25
    elif is_rsi_hot:                                        return 38
    else:                                                   return 50


def _compute_score_adjustment(f, community_raw):
    adj = 0
    if f["is_supply_fear"]:              adj += 8
    if f["foreign_score"] >= SCORE_FOREIGN_STRONG: adj += 4
    if f["vol_score"]     >= SCORE_VOL_STRONG:     adj += 4
    if f["obv_score"]     >= SCORE_OBV_STRONG:     adj += 3
    if f["is_fomo_hot"]:                  adj -= 7
    if community_raw >= SCORE_COMMUNITY_HIGH: adj += 4
    if community_raw <= SCORE_COMMUNITY_LOW:  adj -= 4
    if f["is_high_drawdown"]: adj += 5
    return max(SCORE_ADJ_MIN, min(SCORE_ADJ_MAX, adj))


def calculate_final_score(obj_indicators, community_raw, is_kosdaq, fomo_score):
    flags = _extract_score_flags(obj_indicators, fomo_score)
    base = _determine_base_score(flags)
    adj = _compute_score_adjustment(flags, community_raw)
    kosdaq_adj = SCORE_KOSDAQ_ADJ if is_kosdaq else 0
    final_scream_score = int(max(SCORE_FINAL_MIN, min(SCORE_FINAL_MAX, base + adj + kosdaq_adj)))

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

    return final_scream_score, scream_tier


def get_entry_signal(obj_indicators, final_scream_score, risk_levels=None):
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
    rr_poor         = risk_levels is not None and risk_levels["rr_ratio"] < 1.5 and risk_levels["rr_ratio"] > 0

    if is_fear_zone and is_fg_turning and is_obv_bullish and not rr_poor:
        return {"level": "🟢 진입 적극 고려", "color": "#22c55e",
                "desc": "공포 + 외국인 전환 + OBV 매집 + 손익비 양호. 최적 타점",
                "action": "분할매수 1차 진입"}
    elif is_fear_zone and is_fg_turning and is_obv_bullish and rr_poor:
        return {"level": "🟡 조건부 진입", "color": "#eab308",
                "desc": "수급 신호는 양호하나 손익비 미흡 — 목표가 대비 리스크 과다",
                "action": "손절가 재점검 후 소량 진입"}
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