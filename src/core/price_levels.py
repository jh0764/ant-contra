
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


