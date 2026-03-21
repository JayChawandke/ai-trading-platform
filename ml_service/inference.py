from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import os
import torch
import yfinance as yf
import pandas as pd
import numpy as np
import joblib
from apscheduler.schedulers.background import BackgroundScheduler
import train 
from model import TradingModel

HAS_TORCH = True

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances
model = None
xgb_model = None

def load_models():
    global model, xgb_model
    
    # LSTM Load
    model_path = "model.pt"
    try:
        model = TradingModel(input_size=15)
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path))
            model.eval()
            print("Successfully loaded model.pt")
    except Exception as e:
        print(f"Error loading LSTM: {e}")
        model = None

    # XGBoost Load
    xgb_path = "xgb_model.joblib"
    try:
        if os.path.exists(xgb_path):
            xgb_model = joblib.load(xgb_path)
            print("Successfully loaded xgb_model.joblib")
    except Exception as e:
        print(f"Error loading XGBoost: {e}")
        xgb_model = None

def run_retraining():
    print("Scheduled job: Starting weekly model retraining...")
    try:
        train.train()
        load_models()
        print("Scheduled job: Retraining and model reload complete.")
    except Exception as e:
        print(f"Scheduled job: Retraining failed: {e}")

@app.on_event("startup")
def startup_event():
    load_models()
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_retraining, 'cron', day_of_week='sun', hour=0, minute=0)
    scheduler.start()
    print("APScheduler started: Weekly retraining job configured (Sun 00:00)")

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ema(prices, period=20):
    return prices.ewm(span=period, adjust=False).mean()

def calculate_atr(df, period=14):
    df.columns = [c.lower() for c in df.columns]
    h_l = df['high'] - df['low']
    h_pc = abs(df['high'] - df['close'].shift(1))
    l_pc = abs(df['low'] - df['close'].shift(1))
    tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd, macd_signal

def calculate_stoch(df, period=14, k=3):
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min)
    return stoch_k.rolling(window=k).mean()

def calculate_obv(df):
    obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    return obv

def calculate_roc(prices, period=10):
    return ((prices - prices.shift(period)) / prices.shift(period)) * 100

def compute_features(df):
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).lower() for c in df.columns]
    
    df['momentum'] = df['close'].pct_change()
    df['rsi_14'] = calculate_rsi(df['close'], period=14)
    df['ema_20_gap'] = (df['close'] - calculate_ema(df['close'], 20)) / calculate_ema(df['close'], 20)
    df['vol_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
    df['atr_14'] = calculate_atr(df, period=14) / df['close']
    
    macd, macd_sig = calculate_macd(df['close'])
    df['macd'] = macd
    df['macd_sig'] = macd_sig
    df['stoch_k'] = calculate_stoch(df)
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum() / 1e6
    df['roc_10'] = calculate_roc(df['close'], 10)
    df['ema_50_gap'] = (df['close'] - calculate_ema(df['close'], 50)) / calculate_ema(df['close'], 50)
    df['high_low_gap'] = (df['high'] - df['low']) / df['close']
    df['close_range'] = (df['close'] - df['low']) / (df['high'] - df['low'])
    df['volume_momentum'] = df['volume'].pct_change()
    df['day_index'] = np.arange(len(df)) % 5
    
    features = ['momentum', 'rsi_14', 'ema_20_gap', 'vol_ratio', 'atr_14', 
                'macd', 'macd_sig', 'stoch_k', 'obv', 'roc_10', 
                'ema_50_gap', 'high_low_gap', 'close_range', 'volume_momentum', 'day_index']
    
    return df[features + ['close']].replace([np.inf, -np.inf], np.nan).fillna(0)

def format_signal(prob_up: float, features: dict, symbol: str) -> dict:
    confidence = max(prob_up, 1 - prob_up)
    direction = "BUY" if prob_up > 0.5 else "SELL"
    
    if confidence < 0.65:
        return {
            "symbol": symbol, "prediction": "HOLD", "confidence": round(confidence * 100),
            "headline": "Neutral", "why": ["Consolidation phase detected", "Insufficient conviction"],
            "risk": "Low", "horizon": "Wait", "price_levels": {}
        }

    strength = "Strong" if confidence > 0.80 else "Moderate"
    rsi = features.get('rsi_14', 50)
    ema_gap = features.get('ema_20_gap', 0) * 100
    vol_ratio = features.get('vol_ratio', 1)
    
    why = []
    if direction == "BUY":
        if rsi < 35: why.append(f"RSI at {round(rsi,1)} — oversold bounce")
        if ema_gap < -3: why.append(f"Price {round(abs(ema_gap),1)}% below 20-EMA")
        if vol_ratio > 1.2: why.append(f"High buying volume detected")
    else:
        if rsi > 65: why.append(f"RSI at {round(rsi,1)} — overbought extension")
        if ema_gap > 3: why.append(f"Price {round(ema_gap,1)}% above 20-EMA")
        if vol_ratio > 1.2: why.append(f"Selling pressure increasing")

    if not why: why = ["Trend alignment confirmed by models", "High neural conviction"]

    close = features.get('close', 0)
    atr = (features.get('atr_14', 0) * close) if close > 0 else 0
    
    if direction == "BUY":
        target = round(close + (atr * 3.5), 2)
        stop = round(close - (atr * 2.0), 2)
    else:
        target = round(close - (atr * 3.5), 2)
        stop = round(close + (atr * 2.0), 2)

    return {
        "symbol": symbol, "prediction": direction, "confidence": round(confidence * 100),
        "headline": f"{strength} {direction}", "why": why[:3],
        "risk": "High" if features.get('atr_14', 0) > 0.03 else "Medium",
        "horizon": "Swing · 3-7 Days",
        "price_levels": {"entry": str(round(close, 2)), "target": str(target), "stop": str(stop)},
        "components": {
            "lstm": {"verdict": "Bullish" if prob_up > 0.6 else "Bearish" if prob_up < 0.4 else "Neutral", "score": round(prob_up, 2)},
            "rsi": {"verdict": "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral", "score": round((rsi-50)/50, 2)},
            "volume": {"verdict": "Bullish" if vol_ratio > 1.2 else "Neutral", "score": round(vol_ratio - 1, 2)}
        }
    }

@app.get("/predict/{symbol}")
def predict(symbol: str):
    try:
        # Standardize symbol logic (similar to backend utils)
        s = symbol.upper().strip()
        us_stocks = ["AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "NFLX", "AMD", "INTC", "PYPL", "ADBE", "BA", "DIS", "SPY", "QQQ"]
        
        if s.startswith("^") or s in us_stocks or "." in s:
            yf_symbol = s
        elif s.isdigit():
            yf_symbol = f"{s}.BO"
        else:
            yf_symbol = f"{s}.NS"

        df = yf.download(yf_symbol, period="200d", progress=False)
        if df.empty or len(df) < 100:
            return {"symbol": symbol, "prediction": "HOLD", "confidence": 50, "headline": "No Data", "why": [f"Insufficient history for {yf_symbol}"]}
            
        feat_df = compute_features(df)
        last_row = feat_df.iloc[-1].to_dict()
        
        # LSTM
        lstm_prob = 0.5
        if model:
            seq = feat_df.tail(60).drop(columns=['close']).values
            input_tensor = torch.FloatTensor(seq).unsqueeze(0)
            with torch.no_grad():
                lstm_p = torch.softmax(model(input_tensor), dim=-1)
                lstm_prob = lstm_p[0][1].item()
                
        # XGB
        xgb_prob = 0.5
        if xgb_model:
            latest = feat_df.tail(1).drop(columns=['close']).values
            xgb_prob = float(xgb_model.predict_proba(latest)[0][1])
            
        prob_up = (lstm_prob * 0.45) + (xgb_prob * 0.55) if model and xgb_model else (lstm_prob if model else xgb_prob)
        return format_signal(prob_up, last_row, symbol)
    except Exception as e:
        return {"symbol": symbol, "prediction": "HOLD", "confidence": 0, "headline": "Error", "why": [str(e)]}
