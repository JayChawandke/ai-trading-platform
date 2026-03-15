import asyncio
import yfinance as yf
from typing import Set, Dict
import json
from datetime import datetime
from ..database import SessionLocal
from ..models.watchlist import Watchlist
from ..utils import get_query_symbol

# In-memory store of active symbols (refreshed periodically)
active_symbols: Set[str] = set()
# Cache of latest quotes
latest_quotes: Dict[str, dict] = {}

async def update_active_symbols():
    """Refresh the set of symbols from all users' watchlists."""
    while True:
        db = SessionLocal()
        try:
            symbols = db.query(Watchlist.symbol).distinct().all()
            active_symbols.clear()
            active_symbols.update(s[0] for s in symbols)
        finally:
            db.close()
        await asyncio.sleep(10)  # update every 10 seconds

async def fetch_quotes():
    """Fetch real-time quotes for all active symbols and store them."""
    if not active_symbols:
        return
    
    tickers_map = {s: get_query_symbol(s) for s in active_symbols}
    tickers_str = " ".join(tickers_map.values())
    
    try:
        # Wrap the synchronous yfinance call to run in an executor
        tickers = await asyncio.to_thread(yf.Tickers, tickers_str)
        
        for sym, query_sym in tickers_map.items():
            ticker = tickers.tickers.get(query_sym)
            info = None
            if ticker and ticker.info:
                info = ticker.info
            
            # FALLBACK: If bulk fetch returned empty info, try fetching single ticker (slower but more resilient)
            if not info or not info.get("regularMarketPrice"):
                print(f"JAY DEBUG: Bulk fetch failed for {sym}/{query_sym}. Attempting single fallback.")
                single_ticker = await asyncio.to_thread(yf.Ticker, query_sym)
                info = single_ticker.info
                
            if info:
                # Try to get market data from info
                ltp = info.get("currentPrice", info.get("regularMarketPrice", info.get("previousClose", 0.0)))
                # If it's still 0.0, check other common keys or use history fallback
                if not ltp or ltp == 0.0:
                    ltp = info.get("navPrice", info.get("priceToBook", 0.0))
                
                # FINAL FALLBACK for Indices and Rate Limits: Fetch last 1-day close
                if not ltp or ltp == 0.0:
                    print(f"JAY DEBUG: Fetching history fallback for {sym}")
                    h = await asyncio.to_thread(lambda: yf.Ticker(query_sym).history(period="1d"))
                    if not h.empty:
                        ltp = h["Close"].iloc[-1]
                        # Mock changes if we don't have them
                        chg = ltp - h["Open"].iloc[-1]
                        chg_pct = (chg / h["Open"].iloc[-1]) * 100
                    else:
                        ltp, chg, chg_pct = 0.0, 0.0, 0.0
                else:
                    chg = info.get("regularMarketChange", 0.0)
                    chg_pct = info.get("regularMarketChangePercent", 0.0)
                
                quote = {
                    "symbol": sym,
                    "ltp": float(ltp) if ltp is not None else 0.0,
                    "chg": float(chg) if chg is not None else 0.0,
                    "chg_pct": float(chg_pct) if chg_pct is not None else 0.0,
                    "bid": info.get("bid", 0.0) or 0.0,
                    "bid_size": info.get("bidSize", 0) or 0,
                    "ask": info.get("ask", 0.0) or 0.0,
                    "ask_size": info.get("askSize", 0) or 0,
                    "volume": info.get("volume", 0) or 0,
                    "timestamp": datetime.utcnow().isoformat()
                }
                latest_quotes[sym] = quote
    except Exception as e:
        print(f"JAY DEBUG: Yahoo fetch error: {e}")
