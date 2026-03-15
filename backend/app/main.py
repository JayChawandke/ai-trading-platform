from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .models.trade import Trade
from .models.user import User
from .models.stock import Stock
from .models.watchlist import Watchlist as WatchlistModel
from .database import engine, Base, SessionLocal
from .routers import market, strategy, auth, ws, watchlist, trade as trade_router
import random
import yfinance as yf
import pandas as pd
import numpy as np
from .utils import get_query_symbol

# Create database tables
Base.metadata.create_all(bind=engine)

def seed_stocks(db: Session):
    if db.query(Stock).count() == 0:
        symbols = [
            # Indian Stocks
            {"symbol": "TATAELXSI", "name": "Tata Elxsi", "exchange": "NSE"},
            {"symbol": "TATAPOWER", "name": "Tata Power", "exchange": "NSE"},
            {"symbol": "SBIN", "name": "State Bank of India", "exchange": "NSE"},
            {"symbol": "ICICIBANK", "name": "ICICI Bank", "exchange": "NSE"},
            {"symbol": "RELIANCE", "name": "Reliance Industries", "exchange": "NSE"},
            {"symbol": "TCS", "name": "TCS", "exchange": "NSE"},
            {"symbol": "INFY", "name": "Infosys", "exchange": "NSE"},
            {"symbol": "HDFCBANK", "name": "HDFC Bank", "exchange": "NSE"},
            {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto", "exchange": "NSE"},
            {"symbol": "TATAMOTORS", "name": "Tata Motors", "exchange": "NSE"},
            {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "exchange": "NSE"},
            # US Stocks & Indices
            {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
            {"symbol": "NVDA", "name": "NVIDIA", "exchange": "NASDAQ"},
            {"symbol": "TSLA", "name": "Tesla", "exchange": "NASDAQ"},
            {"symbol": "MSFT", "name": "Microsoft", "exchange": "NASDAQ"},
            {"symbol": "AMZN", "name": "Amazon", "exchange": "NASDAQ"},
            {"symbol": "META", "name": "Meta Platforms", "exchange": "NASDAQ"},
            {"symbol": "AMD", "name": "AMD", "exchange": "NASDAQ"},
            {"symbol": "NFLX", "name": "Netflix", "exchange": "NASDAQ"},
            {"symbol": "^GSPC", "name": "S&P 500", "exchange": "INDEX"},
            {"symbol": "^IXIC", "name": "Nasdaq 100", "exchange": "INDEX"},
            {"symbol": "^NSEI", "name": "Nifty 50", "exchange": "INDEX"},
            {"symbol": "^BSESN", "name": "BSE Sensex", "exchange": "INDEX"}
        ]
        for s in symbols:
            db.add(Stock(**s))
            
        # Seed watchlist for user 1
        initial_watchlist = ["TATAELXSI", "TATAPOWER", "RELIANCE", "AAPL", "NVDA", "TSLA", "^NSEI", "^GSPC"]
        for sym in initial_watchlist:
            db.add(WatchlistModel(user_id=1, symbol=sym))
        db.commit()

with SessionLocal() as db:
    seed_stocks(db)

app = FastAPI(title="AI Trading Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status":"ok"}

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@app.get("/predict/{symbol}")
def get_prediction(symbol: str):
    """Provides a reasoned trading signal based on manual technical analysis."""
    try:
        query_sym = get_query_symbol(symbol)
        
        # Fetch 60 days of data for technical analysis
        ticker = yf.Ticker(query_sym)
        df = ticker.history(period="60d")
        
        if df.empty or len(df) < 20:
            return {"symbol": symbol, "prediction": "HOLD", "confidence": 0.5, "reason": "Insufficient market data for structural analysis."}

        # Manual technical indicators
        close = df["Close"]
        rsi_series = calculate_rsi(close)
        rsi = rsi_series.iloc[-1]
        
        ema20 = close.ewm(span=20, adjust=False).mean()
        sma50 = close.rolling(window=50).mean()
        
        curr_price = close.iloc[-1]
        curr_ema20 = ema20.iloc[-1]
        curr_sma50 = sma50.iloc[-1]
        
        # Trend check
        is_bullish = curr_price > curr_ema20 and curr_price > curr_sma50
        is_bearish = curr_price < curr_ema20 and curr_price < curr_sma50

        # Metadata for reasoning
        ema_dist = ((curr_price - curr_ema20) / curr_ema20) * 100
        sma_dist = ((curr_price - curr_sma50) / curr_sma50) * 100

        prediction = "HOLD"
        reason = f"Market for {symbol} is in a consolidation phase with RSI at {rsi:.1f}."
        confidence = 0.60

        # Detailed Reasoning Logic
        if rsi < 30:
            prediction = "BUY"
            reason = f"Strong Buy Signal for {symbol}: RSI at {rsi:.1f} indicates deep oversold conditions. Price is {abs(ema_dist):.1f}% below 20 EMA, suggesting a reversal."
            confidence = 0.88
        elif rsi > 70:
            prediction = "SELL"
            reason = f"Strong Sell Signal for {symbol}: RSI at {rsi:.1f} indicates overbought conditions. Price is {ema_dist:.1f}% above 20 EMA, momentum is overextended."
            confidence = 0.85
        elif is_bullish:
            prediction = "BUY"
            trend_str = "Strong Uptrend" if curr_ema20 > curr_sma50 else "Recovery Phase"
            reason = f"{trend_str} in {symbol}: Price is {ema_dist:.1f}% above 20 EMA and {sma_dist:.1f}% above 50 SMA. Bullish momentum maintained."
            confidence = 0.76
        elif is_bearish:
            prediction = "SELL"
            trend_str = "Strong Downtrend" if curr_ema20 < curr_sma50 else "Distribution Phase"
            reason = f"{trend_str} in {symbol}: Price is {abs(ema_dist):.1f}% below 20 EMA and {abs(sma_dist):.1f}% below 50 SMA. Resistance at top heavy."
            confidence = 0.79
        else:
            if rsi > 50:
                reason = f"Neutral-Bullish for {symbol}: RSI at {rsi:.1f} shows slight upward bias. Price has minor support at {curr_ema20:.2f}."
            else:
                reason = f"Neutral-Bearish for {symbol}: RSI at {rsi:.1f} suggests weakening momentum heading towards support levels."

        return {
            "symbol": symbol,
            "prediction": prediction,
            "confidence": round(confidence, 2),
            "reason": reason
        }
    except Exception as e:
        return {"symbol": symbol, "prediction": "HOLD", "confidence": 0.5, "reason": f"Signal error: {str(e)}"}

app.include_router(market.router, prefix="/market")
app.include_router(strategy.router, prefix="/strategy")
app.include_router(auth.router, prefix="/auth")
app.include_router(ws.router)
app.include_router(watchlist.router, prefix="/watchlist")
app.include_router(trade_router.router, prefix="/trade")
