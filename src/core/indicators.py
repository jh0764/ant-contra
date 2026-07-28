import pandas as pd
import numpy as np
from core.candle_patterns import detect_patterns, score_patterns
from constants import (
    RSI_OVERSOLD, RSI_WEAK_RECOVERY, RSI_OVERBOUGHT,
    BB_LOWER_NEAR_PCT, BB_UPPER_NEAR_PCT,
    W52_LOW_NEAR_PCT, W52_HIGH_NEAR_PCT, W52_LOW_ZONE_PCT,
    DRAWDOWN_DEEP, DRAWDOWN_SIGNIFICANT, DRAWDOWN_MODERATE, DRAWDOWN_NEAR_HIGH,
    VOL_SURGE_RATIO, VOL_DEAD_RATIO, VOL_MICRO_CAP_THRESHOLD_EOK,
)

def calculate_objective_indicators(close_series, volume_series, foreign_data, news_data, is_kosdaq,
                                    high_series=None, low_series=None, rs_data=None, open_series=None):
    results = {}

    #RSI (14일)
    try:
        delta = close_series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-9)
        rsi_val = float(100 - (100 / (1 + rs.iloc[-1])))
        if rsi_val <= RSI_OVERSOLD:
            rsi_status, rsi_label = "green", f"RSI {rsi_val:.1f} — 과매도 극단 구간"
            rsi_desc, rsi_score = "통계적 바닥 근접. 역발상 매수 우위 신호", 15
        elif rsi_val <= RSI_WEAK_RECOVERY:
            rsi_status, rsi_label = "yellow", f"RSI {rsi_val:.1f} — 약세 회복 구간"
            rsi_desc, rsi_score = "과매도 직후 회복 중. 추이 관찰 필요", 7
        elif rsi_val >= RSI_OVERBOUGHT:
            rsi_status, rsi_label = "red", f"RSI {rsi_val:.1f} — 과매수 과열 구간"
            rsi_desc, rsi_score = "단기 고점 가능성. 역발상 매수 불리", -5
        else:
            rsi_status, rsi_label = "yellow", f"RSI {rsi_val:.1f} — 중립 구간"
            rsi_desc, rsi_score = "과매도·과매수 어느 쪽도 아님. 대기", 0
        results["rsi"] = {"status": rsi_status, "label": rsi_label, "desc": rsi_desc, "score": rsi_score, "value": rsi_val}
    except Exception:
        results["rsi"] = {"status": "yellow", "label": "RSI — 계산 불가", "desc": "데이터 부족", "score": 0, "value": None}

    #볼린저 밴드(20일, 2σ)
    try:
        ma20 = close_series.rolling(20).mean()
        std20 = close_series.rolling(20).std()
        upper = ma20 + 2 * std20
        lower = ma20 - 2 * std20
        current = float(close_series.iloc[-1])
        lower_val = float(lower.iloc[-1])
        upper_val = float(upper.iloc[-1])
        band_width = upper_val - lower_val
        position_pct = ((current - lower_val) / band_width * 100) if band_width > 0 else 50
        if current <= lower_val:
            bb_status, bb_label = "green", f"볼린저 하단 이탈 ({position_pct:.0f}%)"
            bb_desc, bb_score = "통계적으로 2.3%만 해당하는 극단 하락 구간", 15
        elif position_pct <= BB_LOWER_NEAR_PCT:
            bb_status, bb_label = "green", f"볼린저 하단 근접 ({position_pct:.0f}%)"
            bb_desc, bb_score = "하단 밴드 근접 중. 반등 가능성 높은 구간", 8
        elif position_pct >= BB_UPPER_NEAR_PCT:
            bb_status, bb_label = "red", f"볼린저 상단 근접 ({position_pct:.0f}%)"
            bb_desc, bb_score = "상단 밴드 근접. 단기 과열 구간", -5
        else:
            bb_status, bb_label = "yellow", f"볼린저 중립 구간 ({position_pct:.0f}%)"
            bb_desc, bb_score = "밴드 중간 위치. 방향성 대기 중", 0
        results["bb"] = {"status": bb_status, "label": bb_label, "desc": bb_desc, "score": bb_score}
    except Exception:
        results["bb"] = {"status": "yellow", "label": "볼린저 밴드 — 계산 불가", "desc": "데이터 부족", "score": 0}

    #52주 신저가/신고가 근접도 (양방향)
    try:
        week52_low = float(close_series.min())
        week52_high = float(close_series.max())
        current = float(close_series.iloc[-1])
        gap_from_low_pct = ((current - week52_low) / week52_low) * 100
        gap_from_high_pct = ((week52_high - current) / week52_high) * 100
        if gap_from_low_pct <= W52_LOW_NEAR_PCT:
            w52_status, w52_label = "green", f"52주 신저가 +{gap_from_low_pct:.1f}%"
            w52_desc, w52_score = "신저가 5% 이내. 역발상 매수 최적 구간", 12
        elif gap_from_high_pct <= W52_HIGH_NEAR_PCT:
            w52_status, w52_label = "red", f"52주 신고가 근접 (-{gap_from_high_pct:.1f}%)"
            w52_desc, w52_score = "신고가 구간. 공포 아닌 과열 국면. 추격 위험", -10
        elif gap_from_low_pct <= W52_LOW_ZONE_PCT:
            w52_status, w52_label = "yellow", f"52주 저가 +{gap_from_low_pct:.1f}%"
            w52_desc, w52_score = "저점 영역 내 위치", 4
        else:
            w52_status, w52_label = "yellow", f"52주 고가 대비 -{gap_from_high_pct:.1f}%"
            w52_desc, w52_score = "중립 구간", 0
        results["w52"] = {"status": w52_status, "label": w52_label, "desc": w52_desc, "score": w52_score}
    except Exception:
        results["w52"] = {"status": "yellow", "label": "52주 데이터 — 계산 불가", "desc": "데이터 부족", "score": 0}

    #고점 대비 낙폭 (Drawdown from 52W High)
    try:
        week52_high = float(close_series.max())
        current = float(close_series.iloc[-1])
        drawdown_pct = (week52_high - current) / week52_high * 100
        if drawdown_pct >= DRAWDOWN_DEEP:
            dd_status, dd_label = "green", f"고점 대비 -{drawdown_pct:.1f}% (대낙폭)"
            dd_desc, dd_score = "장기 투자자 손실 구간. 역발상 유효", 15
        elif drawdown_pct >= DRAWDOWN_SIGNIFICANT:
            dd_status, dd_label = "green", f"고점 대비 -{drawdown_pct:.1f}%"
            dd_desc, dd_score = "유의미한 조정 구간", 8
        elif drawdown_pct >= DRAWDOWN_MODERATE:
            dd_status, dd_label = "yellow", f"고점 대비 -{drawdown_pct:.1f}%"
            dd_desc, dd_score = "중간 조정. 추세 확인 필요", 3
        elif drawdown_pct <= DRAWDOWN_NEAR_HIGH:
            dd_status, dd_label = "red", f"고점 근접 -{drawdown_pct:.1f}%"
            dd_desc, dd_score = "신고가 부근. 역발상 불리", -10
        else:
            dd_status, dd_label = "yellow", f"고점 대비 -{drawdown_pct:.1f}%"
            dd_desc, dd_score = "중립 구간", 0
        results["drawdown"] = {"status": dd_status, "label": dd_label, "desc": dd_desc, "score": dd_score, "value": drawdown_pct}
    except Exception:
        results["drawdown"] = {"status": "yellow", "label": "낙폭 — 계산 불가", "desc": "데이터 부족", "score": 0, "value": 0}

    # 장기추세 필터 (200일선 위치 + 200일선 기울기) — 눌림목 vs 낙폭과대(떨어지는 칼날) 구분
    try:
        if len(close_series) < 210:
            raise ValueError("데이터 부족 (200일치 미만)")
        ma200 = close_series.rolling(200).mean()
        current = float(close_series.iloc[-1])
        ma200_now = float(ma200.iloc[-1])
        ma200_prev = float(ma200.iloc[-20])
        slope_pct = (ma200_now - ma200_prev) / ma200_prev * 100
        is_below_ma200 = current < ma200_now
        is_ma_declining = slope_pct <= -0.5

        if is_below_ma200 and is_ma_declining:
            trend_status, trend_label = "red", f"200일선 하향 이탈 (기울기 {slope_pct:+.1f}%)"
            trend_desc = "장기 추세 자체가 무너진 구간 — '떨어지는 칼날' 주의. 역발상 매수 근거 약함"
            trend_score = -10
        elif is_below_ma200 and not is_ma_declining:
            trend_status, trend_label = "green", f"200일선 위/횡보 중 단기 이탈 (기울기 {slope_pct:+.1f}%)"
            trend_desc = "장기 상승추세는 유지된 채 단기 조정 — 눌림목 성격, 역발상 신뢰도 높음"
            trend_score = 10
        elif not is_below_ma200 and is_ma_declining:
            trend_status, trend_label = "yellow", f"200일선 하락 중, 현재가는 위 (기울기 {slope_pct:+.1f}%)"
            trend_desc = "추세 전환 초기 또는 단기 반등 — 추가 확인 필요"
            trend_score = 0
        else:
            trend_status, trend_label = "yellow", f"장기 상승추세 유지 (기울기 {slope_pct:+.1f}%)"
            trend_desc = "구조적 강세 지속 중 — 공포 매수 국면 아님"
            trend_score = -3

        results["trend"] = {
            "status": trend_status, "label": trend_label, "desc": trend_desc, "score": trend_score,
            "is_structural_downtrend": (trend_status == "red"),
        }
    except Exception:
        results["trend"] = {"status": "yellow", "label": "장기추세 — 계산 불가", "desc": "200일치 데이터 부족", "score": 0, "is_structural_downtrend": False}

    # 캔들패턴 인식 (시가 데이터 필요, 없으면 스킵)
    try:
        if open_series is None:
            raise ValueError("시가 데이터 없음")
        patterns = detect_patterns(open_series, high_series, low_series, close_series)
        results["candle"] = score_patterns(patterns)
    except Exception:
        results["candle"] = {"status": "yellow", "label": "캔들패턴 — 계산 불가", "desc": "시가 데이터 부족", "score": 0}

    #일목균형표 구름대 이탈
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
                ich_desc, ich_score = "구조적 하락 국면. 역발상 관찰 구간", min(12, 4 + depth_pct)
            elif current > cloud_top:
                ich_status, ich_label = "red", "구름대 상단 위 (추세 상승)"
                ich_desc, ich_score = "구조적 상승 국면. 역발상 불리", -6
            else:
                ich_status, ich_label = "yellow", "구름대 내부 (혼조)"
                ich_desc, ich_score = "추세 방향성 불명확", 0
            results["ichimoku"] = {"status": ich_status, "label": ich_label, "desc": ich_desc, "score": int(ich_score)}
        else:
            raise ValueError("데이터 부족")
    except Exception:
        results["ichimoku"] = {"status": "yellow", "label": "일목균형표 — 계산 불가", "desc": "데이터 부족", "score": 0}

    #거래량 + 거래대금 결합 수급 강도
    try:
        vol_today = float(volume_series.iloc[-1])
        vol_avg20 = float(volume_series.rolling(20).mean().iloc[-1])
        vol_ratio = vol_today / vol_avg20 if vol_avg20 > 0 else 1.0
        price_today = float(close_series.iloc[-1])
        price_prev = float(close_series.iloc[-2])
        price_chg = (price_today - price_prev) / price_prev
        turnover_today = vol_today * price_today / 1e8
        is_micro = turnover_today < VOL_MICRO_CAP_THRESHOLD_EOK
        capped_ratio = min(vol_ratio, 3.0) if is_micro else vol_ratio
        if capped_ratio >= VOL_SURGE_RATIO and price_chg < -0.01:
            vol_status = "green"
            vol_label = f"거래량 {capped_ratio:.1f}배 + 하락 — 투매 ({turnover_today:.0f}억)"
            vol_desc = f"패닉셀 수급 ({turnover_today:.0f}억원). 바닥 신호 유력"
            vol_score = 14 if turnover_today >= 100 else 8
        elif capped_ratio >= VOL_SURGE_RATIO and price_chg > 0.01:
            vol_status = "red"
            vol_label = f"거래량 {capped_ratio:.1f}배 + 상승 — 추격 ({turnover_today:.0f}억)"
            vol_desc = "상승 동반 대량 거래 = 추격 위험"
            vol_score = -8
        elif capped_ratio <= VOL_DEAD_RATIO:
            vol_status = "yellow"
            vol_label = f"거래량 {capped_ratio:.1f}배 — 무기력 ({turnover_today:.0f}억)"
            vol_desc = "투항 후 무관심 구간"
            vol_score = 3
        else:
            vol_status = "yellow"
            vol_label = f"거래량 {capped_ratio:.1f}배 / {turnover_today:.0f}억"
            vol_desc = "특이 신호 없음"
            vol_score = 0
        results["volume"] = {"status": vol_status, "label": vol_label, "desc": vol_desc, "score": vol_score, "turnover": turnover_today}
    except Exception:
        results["volume"] = {"status": "yellow", "label": "거래량 — 계산 불가", "desc": "데이터 부족", "score": 0}

    #OBV 다이버전스 (매집/분산 감지)
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
            obv_desc, obv_score = "가격 저점인데 거래량은 안 빠짐 = 매집 정황", 15
        elif p_pos >= 85 and o_pos <= 55:
            obv_status, obv_label = "red", f"약세 다이버전스 (가격{p_pos:.0f}%/OBV{o_pos:.0f}%)"
            obv_desc, obv_score = "고점인데 거래량 뒷받침 약함 = 분산 정황", -8
        else:
            obv_status, obv_label = "yellow", f"다이버전스 없음 ({p_pos:.0f}%/{o_pos:.0f}%)"
            obv_desc, obv_score = "가격·거래량 동행 중", 0
        results["obv"] = {"status": obv_status, "label": obv_label, "desc": obv_desc, "score": obv_score}
    except Exception:
        results["obv"] = {"status": "yellow", "label": "OBV — 계산 불가", "desc": "데이터 부족", "score": 0}

    # 외국인 순매수 (naver_scraper.get_foreign_net_buying 결과 사용)
    try:
        if "error" in foreign_data:
            raise ValueError(foreign_data["error"])
        net_values = foreign_data["net_values"]
        consec_sell = foreign_data["consec_sell"]
        consec_buy = foreign_data["consec_buy"]
        recent_sum = foreign_data["recent_sum"]
        is_turning = foreign_data["is_turning"]
        is_still_selling = foreign_data["is_still_selling"]

        if is_turning:
            fg_status, fg_label = "green", f"외국인 매도→매수 전환 ({net_values[0]//100:+,}억)"
            fg_desc, fg_score = "수급 전환 포착. 역발상 진입 트리거", 15
        elif consec_sell >= 3 and abs(net_values[0]) < abs(net_values[1]):
            fg_status, fg_label = "yellow", f"외국인 매도 둔화 ({recent_sum:+,}억)"
            fg_desc, fg_score = "이탈 속도 감소. 전환 대기 구간", 5
        elif is_still_selling:
            fg_status, fg_label = "red", f"외국인 연속 이탈 ({recent_sum:+,}억)"
            fg_desc, fg_score = "수급 이탈 진행 중. 진입 대기", -8
        elif consec_buy >= 2:
            fg_status, fg_label = "yellow", f"외국인 순매수 중 ({recent_sum:+,}억)"
            fg_desc, fg_score = "외국인 유입. 공포 구간 아님", -3
        else:
            fg_status, fg_label = "yellow", "외국인 혼조세"
            fg_desc, fg_score = "방향성 없음", 0

        results["foreign"] = {
            "status": fg_status, "label": fg_label, "desc": fg_desc, "score": fg_score,
            "is_turning": is_turning, "is_still_selling": is_still_selling
        }
    except Exception as e:
        results["foreign"] = {"status": "yellow", "label": f"외국인 — {str(e)[:45]}", "desc": "잠시 후 재시도", "score": 0}

    #공포-거래량 괴리 지수
    try:
        if len(close_series) >= 6 and len(volume_series) >= 6:
            price_chg_5d = (float(close_series.iloc[-1]) - float(close_series.iloc[-6])) / float(close_series.iloc[-6])
            vol_chg_5d = (float(volume_series.iloc[-1]) - float(volume_series.iloc[-6])) / float(volume_series.iloc[-6])
            if price_chg_5d < -0.03 and vol_chg_5d > 0.5:
                pvd_status, pvd_label = "green", f"패닉셀 감지 (가격↓{price_chg_5d*100:.1f}% / 거래량↑{vol_chg_5d*100:.0f}%)"
                pvd_desc, pvd_score = "하락+거래량 폭발 = 투매 클라이맥스. 바닥 신호 최강", 15
            elif price_chg_5d < -0.03 and vol_chg_5d < -0.2:
                pvd_status, pvd_label = "yellow", f"무관심 하락 (가격↓{price_chg_5d*100:.1f}% / 거래량↓)"
                pvd_desc, pvd_score = "하락+거래량 감소 = 아직 바닥 탐색 중. 대기 권고", 3
            elif price_chg_5d > 0.05 and vol_chg_5d > 0.5:
                pvd_status, pvd_label = "red", f"추격 위험 (가격↑{price_chg_5d*100:.1f}% / 거래량↑{vol_chg_5d*100:.0f}%)"
                pvd_desc, pvd_score = "상승+거래량 폭발 = FOMO 추격 위험 구간", -5
            else:
                pvd_status, pvd_label = "yellow", f"괴리 미포착 (가격{price_chg_5d*100:+.1f}%)"
                pvd_desc, pvd_score = "뚜렷한 패닉셀/추격 신호 없음", 0
            results["pvd"] = {"status": pvd_status, "label": pvd_label, "desc": pvd_desc, "score": pvd_score}
        else:
            raise ValueError("데이터 부족")
    except Exception:
        results["pvd"] = {"status": "yellow", "label": "괴리 지수 — 계산 불가", "desc": "데이터 부족", "score": 0}

    # 뉴스 공백 (naver_scraper.get_news_vacuum 결과 사용)
    try:
        if "error" in news_data:
            raise ValueError(news_data["error"])
        today_count = news_data["today_count"]
        today_ratio = news_data["today_ratio"]

        if today_count == 0:
            nv_status, nv_label = "green", "뉴스 완전 공백 — 관심 소멸"
            nv_desc, nv_score = "미디어 무관심 극대화. 역발상 저점 신호", 8
        elif today_ratio <= 0.15:
            nv_status, nv_label = "green", f"뉴스 희소 (당일 {today_count}건)"
            nv_desc, nv_score = "언론 관심 낮음. 조용한 바닥 구간 가능", 4
        elif today_ratio >= 0.6:
            nv_status, nv_label = "red", f"뉴스 폭발 (당일 {today_count}건)"
            nv_desc, nv_score = "미디어 과열 = 대중 관심 극대 = 고점 경계", -5
        else:
            nv_status, nv_label = "yellow", f"뉴스 보통 (당일 {today_count}건)"
            nv_desc, nv_score = "정상 수준 언론 관심", 0
        results["news_vacuum"] = {"status": nv_status, "label": nv_label, "desc": nv_desc, "score": nv_score}
    except Exception:
        results["news_vacuum"] = {"status": "yellow", "label": "뉴스 지수 — 수집 불가", "desc": "잠시 후 재시도", "score": 0}

    if rs_data is not None:
        results["rs"] = rs_data
    price_keys_score = sum(results.get(k, {}).get("score", 0) for k in ["rsi", "bb", "w52", "ichimoku", "rs", "trend", "candle"])
    supply_keys_score = sum(results.get(k, {}).get("score", 0) for k in ["volume", "foreign", "obv", "pvd"])
    news_score = results.get("news_vacuum", {}).get("score", 0)

    price_normalized = max(-30, min(40, price_keys_score)) * 0.35
    supply_normalized = max(-30, min(40, supply_keys_score)) * 0.40
    news_normalized = max(-10, min(10, news_score)) * 0.25

    raw_obj_score = price_normalized + supply_normalized + news_normalized
    base_offset = 40 if is_kosdaq else 35
    objective_score = int(max(0, min(80, raw_obj_score * 0.7 + base_offset)))

    return results, objective_score