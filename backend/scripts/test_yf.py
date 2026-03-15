
import yfinance as yf
import json

def test_history(symbol):
    query_sym = symbol
    if not symbol.endswith(".NS") and symbol != "AAPL":
        query_sym = f"{symbol}.NS"
    
    print(f"Testing {symbol} as {query_sym}")
    ticker = yf.Ticker(query_sym)
    hist = ticker.history(period="1mo", interval="1d")
    
    if hist.empty:
        print(f"FAILED: No data for {query_sym}")
        return
    
    print(f"SUCCESS: Found {len(hist)} rows")
    # print(hist.tail(2))

if __name__ == "__main__":
    test_history("TATAELXSI")
    test_history("AAPL")
    test_history("SBIN")
