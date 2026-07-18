import pandas as pd
from constants import fear_dictionary, greedy_dictionary
#감성 사전
def analyze_combined_sentiment(naver_posts, close_series=None, high_series=None, low_series=None):
    naver_titles = [p["title"] for p in naver_posts]
    all_texts = naver_titles  
    total_analyzed_posts = max(1, len(all_texts))
    combined = " ".join(all_texts).lower()



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

