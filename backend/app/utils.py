def get_query_symbol(symbol: str):
    """
    Standardizes symbols for Yahoo Finance.
    US Tech: AAPL, NVDA, TSLA, MSFT, GOOGL, AMZN, META, NFLX, AMD, INTC
    Indices: ^GSPC, ^IXIC, ^DJI, ^NSEI, ^BSESN
    """
    s = symbol.upper().strip()
    
    # List of known US stocks that should not have .NS
    us_stocks = [
        "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", 
        "NFLX", "AMD", "INTC", "PYPL", "ADBE", "CSCO", "QCOM", 
        "SPY", "QQQ"
    ]
    
    # Indices or US stocks as is
    if s.startswith("^") or s in us_stocks:
        return s
        
    # Indian stocks usually need .NS suffix
    if not s.endswith(".NS"):
        return f"{s}.NS"
    return s
