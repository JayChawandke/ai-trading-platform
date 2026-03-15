from app.database import SessionLocal
from app.models.stock import Stock
from app.models.watchlist import Watchlist

def seed():
    db = SessionLocal()
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
        if not db.query(Stock).filter_by(symbol=s['symbol']).first():
            db.add(Stock(**s))
            print(f"Added stock: {s['symbol']}")
        
        if not db.query(Watchlist).filter_by(user_id=1, symbol=s['symbol']).first():
            db.add(Watchlist(user_id=1, symbol=s['symbol']))
            print(f"Added to watchlist: {s['symbol']}")
            
    db.commit()
    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
