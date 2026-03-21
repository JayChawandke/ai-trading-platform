
from fastapi import APIRouter
import yfinance as yf
from ..utils import get_query_symbol

router = APIRouter()

@router.get("/price/{symbol}")
def get_price(symbol:str):
    query_sym = get_query_symbol(symbol)
    data = yf.Ticker(query_sym)
    # Use fast_info if available or history for validation
    hist = data.history(period="1d")
    if hist.empty:
         return {"symbol": symbol, "price": 0.0, "error": "Symbol not found"}
    
    price = float(hist["Close"].iloc[-1])
    # Try to get a clean name
    name = symbol
    try:
        info = data.info
        name = info.get("shortName", info.get("longName", symbol))
    except: pass

    return {
        "symbol": symbol, 
        "query_symbol": query_sym,
        "price": price, 
        "name": name,
        "exchange": "UNKNOWN" # Simplified for now
    }

@router.get("/history/{symbol}")
def get_history(symbol: str, period: str = "1mo", interval: str = "1d"):
    query_sym = get_query_symbol(symbol)
    ticker = yf.Ticker(query_sym)
    hist = ticker.history(period=period, interval=interval)
    
    if hist.empty:
        return []
        
    # Format for lightweight-charts: { time: 'YYYY-MM-DD', open: X, high: X, low: X, close: X }
    data = []
    for index, row in hist.iterrows():
        # Handle different intervals (daily uses date, intra-day uses timestamp)
        if interval in ['1d', '5d', '1wk', '1mo', '3mo']:
            time_val = index.strftime('%Y-%m-%d')
        else:
            time_val = int(index.timestamp())

        data.append({
            "time": time_val,
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"])
        })
    return data
