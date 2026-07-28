def _candle_metrics(o, h, l, c):
    body = abs(c - o)
    upper = h - max(c, o)
    lower = min(c, o) - l
    rng = (h - l) if (h - l) > 0 else 1e-9
    return body, upper, lower, rng


def detect_patterns(open_s, high_s, low_s, close_s):
    """
    최근 캔들로 반전 패턴 감지. 최소 6개 캔들 필요(추세 판단용).
    반환: [{"name":.., "type":"bullish"/"bearish", "desc":..}, ...] (여러 개 동시 감지 가능)
    """
    patterns = []
    if len(close_s) < 6:
        return patterns

    o, h, l, c = float(open_s.iloc[-1]), float(high_s.iloc[-1]), float(low_s.iloc[-1]), float(close_s.iloc[-1])
    o1, h1, l1, c1 = float(open_s.iloc[-2]), float(high_s.iloc[-2]), float(low_s.iloc[-2]), float(close_s.iloc[-2])
    body, upper, lower, rng = _candle_metrics(o, h, l, c)
    body1, upper1, lower1, rng1 = _candle_metrics(o1, h1, l1, c1)

    is_downtrend = float(close_s.iloc[-6]) > float(close_s.iloc[-1])
    is_uptrend = float(close_s.iloc[-6]) < float(close_s.iloc[-1])
    wick_floor = max(body, rng * 0.05, 1e-9)

    # 망치형 — 하락 이후 아래꼬리 긴 캔들
    if is_downtrend and lower >= 2 * body and upper <= 0.3 * wick_floor:
        patterns.append({"name": "망치형", "type": "bullish",
                          "desc": "하락 이후 아래꼬리가 긴 캔들 — 저가권 매수세 유입, 단기 반등 가능성"})

    # 상승장악형
    if c1 < o1 and c > o and o <= c1 and c >= o1:
        patterns.append({"name": "상승장악형", "type": "bullish",
                          "desc": "전일 음봉을 완전히 감싸는 양봉 — 매수 우위 전환 신호"})

    # 하락장악형
    if c1 > o1 and c < o and o >= c1 and c <= o1:
        patterns.append({"name": "하락장악형", "type": "bearish",
                          "desc": "전일 양봉을 완전히 감싸는 음봉 — 매도 우위 전환, 상단 경계 신호"})

    # 유성형(역망치) — 상승 이후 윗꼬리 긴 캔들
    if is_uptrend and upper >= 2 * body and lower <= 0.3 * wick_floor:
        patterns.append({"name": "유성형", "type": "bearish",
                          "desc": "상승 이후 윗꼬리가 긴 캔들 — 상단 매도세 유입, 단기 조정 가능성"})

    # 관통형 (2봉)
    if c1 < o1 and body1 > 0 and o <= c1 and c > (o1 + c1) / 2 and c < o1:
        patterns.append({"name": "관통형", "type": "bullish",
                          "desc": "전일 종가 부근에서 출발해 전일 몸통 중간 이상 반등 마감 — 매수세 유입 신호"})

    # 샛별형 (3봉)
    if len(close_s) >= 6:
        o2, h2, l2, c2 = float(open_s.iloc[-3]), float(high_s.iloc[-3]), float(low_s.iloc[-3]), float(close_s.iloc[-3])
        body2, *_ = _candle_metrics(o2, h2, l2, c2)
        mid2 = (o2 + c2) / 2
        if c2 < o2 and body2 > 0 and body1 <= body2 * 0.4 and c > o and c >= mid2:
            patterns.append({"name": "샛별형", "type": "bullish",
                              "desc": "3봉 반전 패턴 — 매도 소진 후 강한 매수 반등, 신뢰도 높은 바닥 신호"})

    return patterns


def score_patterns(patterns):
    """감지된 패턴들 중 가장 강한 신호로 status/score 결정."""
    priority = {
        "샛별형": 12, "상승장악형": 8, "관통형": 7, "망치형": 5,
        "하락장악형": -8, "유성형": -5,
    }
    if not patterns:
        return {"status": "yellow", "label": "특이 캔들패턴 없음", "desc": "일반적인 캔들 형태", "score": 0}

    best = max(patterns, key=lambda p: abs(priority.get(p["name"], 0)))
    score = priority.get(best["name"], 0)
    status = "green" if score > 0 else ("red" if score < 0 else "yellow")
    names = ", ".join(p["name"] for p in patterns)
    return {"status": status, "label": f"{names} 감지", "desc": best["desc"], "score": score}