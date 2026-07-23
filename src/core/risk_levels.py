import pandas as pd

def calculate_risk_levels(close_series, high_series, low_series, current_price):
    try:
        ma20 = close_series.rolling(20).mean()
        std20 = close_series.rolling(20).std()
        bb_lower = float((ma20 - 2 * std20).iloc[-1])
        bb_upper = float((ma20 + 2 * std20).iloc[-1])
        bb_mid = float(ma20.iloc[-1])

        prev_close = close_series.shift(1)
        tr = pd.concat([
            high_series - low_series,
            (high_series - prev_close).abs(),
            (low_series - prev_close).abs()
        ], axis=1).max(axis=1)
        atr14 = float(tr.rolling(14).mean().iloc[-1])

        high, low = float(close_series.max()), float(close_series.min())
        diff = high - low
        fib_618 = high - diff * 0.618  # 하단 지지 후보
        fib_382 = high - diff * 0.382  # 상단 저항 후보

        # 손절 후보 중 현재가에 더 가까운(타이트한) 라인을 채택 → R:R 산출 시 손실 과대평가 방지
        stop_candidates = [c for c in [bb_lower, fib_618] if c > 0 and c < current_price]
        stop_loss = (max(stop_candidates) if stop_candidates else current_price * 0.93) - atr14 * 0.5

        target_candidates = [c for c in [bb_mid, fib_382, bb_upper] if c > current_price]
        target1 = min(target_candidates) if target_candidates else current_price * 1.05
        target2 = max([c for c in [bb_upper, fib_382] if c > current_price], default=target1 * 1.03)

        risk = current_price - stop_loss
        reward = target1 - current_price
        rr_ratio = round(reward / risk, 2) if risk > 0 else 0

        if rr_ratio >= 2.0:
            rr_verdict = "우수"
        elif rr_ratio >= 1.5:
            rr_verdict = "양호"
        elif rr_ratio > 0:
            rr_verdict = "미흡"
        else:
            rr_verdict = "산출불가"

        return {
            "stop_loss": int(stop_loss), "target1": int(target1), "target2": int(target2),
            "rr_ratio": rr_ratio, "rr_verdict": rr_verdict,
            "risk_pct": round(risk / current_price * 100, 1) if current_price else 0,
            "reward_pct": round(reward / current_price * 100, 1) if current_price else 0,
        }
    except Exception:
        return None