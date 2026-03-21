def get_query_symbol(symbol: str):
    """
    Standardizes symbols for Yahoo Finance.
    US Tech: AAPL, NVDA, TSLA, MSFT, GOOGL, AMZN, META, NFLX, AMD, INTC
    Indices: ^GSPC, ^IXIC, ^DJI, ^NSEI, ^BSESN
    """
    s = symbol.upper().strip()
    
    # List of known US stocks/indices that should stay as is
    us_stocks = [
        "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", 
        "NFLX", "AMD", "INTC", "PYPL", "ADBE", "CSCO", "QCOM", 
        "SPY", "QQQ", "BA", "DIS"
    ]
    
    # If it already has a suffix or is a known US stock/index, return as is
    if s.startswith("^") or s in us_stocks or "." in s:
        return s
        
    # Default to NSE for Indian stocks unless it's clearly US (short alphanumeric) 
    # but we already checked us_stocks. 
    # If the user searches '500112', it's likely BSE but yfinance prefers '500112.BO'
    if s.isdigit():
        return f"{s}.BO"

    # Default Indian stock suffix
    return f"{s}.NS"
