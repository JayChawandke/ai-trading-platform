import torch
import torch.nn as nn
import torch.optim as optim
import yfinance as yf
import pandas as pd
import numpy as np
from model import TradingModel
import os
import xgboost as xgb
import joblib
from torch.utils.data import DataLoader, TensorDataset

def compute_features(df):
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).lower() for c in df.columns]
    
    def calculate_rsi(prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_ema(prices, period=20):
        return prices.ewm(span=period, adjust=False).mean()

    def calculate_atr(df, period=14):
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

    def calculate_stoch(df, period=14):
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        return 100 * (df['close'] - low_min) / (high_max - low_min)

    df['momentum'] = df['close'].pct_change()
    df['rsi_14'] = calculate_rsi(df['close'])
    df['ema_20_gap'] = (df['close'] - calculate_ema(df['close'], 20)) / calculate_ema(df['close'], 20)
    df['vol_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
    df['atr_14'] = calculate_atr(df) / df['close']
    
    macd, macd_sig = calculate_macd(df['close'])
    df['macd'] = macd
    df['macd_sig'] = macd_sig
    df['stoch_k'] = calculate_stoch(df)
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum() / 1e6
    df['roc_10'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100
    df['ema_50_gap'] = (df['close'] - calculate_ema(df['close'], 50)) / calculate_ema(df['close'], 50)
    df['high_low_gap'] = (df['high'] - df['low']) / df['close']
    df['close_range'] = (df['close'] - df['low']) / (df['high'] - df['low'])
    df['volume_momentum'] = df['volume'].pct_change()
    df['day_index'] = np.arange(len(df)) % 5
    
    features = ['momentum', 'rsi_14', 'ema_20_gap', 'vol_ratio', 'atr_14', 
                'macd', 'macd_sig', 'stoch_k', 'obv', 'roc_10', 
                'ema_50_gap', 'high_low_gap', 'close_range', 'volume_momentum', 'day_index']
    
    res = df[features + ['close']].copy()
    # Replace Infinity with large numbers and NaN with 0
    res = res.replace([np.inf, -np.inf], np.nan).fillna(0)
    return res

def prepare_data(symbols, seq_len=60):
    all_X = []
    all_y = []
    
    features = ['momentum', 'rsi_14', 'ema_20_gap', 'vol_ratio', 'atr_14', 
                'macd', 'macd_sig', 'stoch_k', 'obv', 'roc_10', 
                'ema_50_gap', 'high_low_gap', 'close_range', 'volume_momentum', 'day_index']

    for symbol in symbols:
        print(f"Fetching data for {symbol}...")
        try:
            df = yf.download(symbol, period="5y", interval="1d", progress=False)
            if df.empty: continue
            
            feat_df = compute_features(df)
            if len(feat_df) < seq_len + 1: continue
            
            target = (feat_df['close'].shift(-1) > feat_df['close']).astype(int).values
            data = feat_df[features].values
            
            for i in range(len(data) - seq_len - 1):
                all_X.append(data[i:i+seq_len])
                all_y.append(target[i+seq_len])
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            
    return np.array(all_X), np.array(all_y)

def train():
    symbols = [
        # US Large Cap
        "AAPL", "NVDA", "TSLA", "MSFT", "GOOGL", "AMZN", "META", "AMD", "NFLX",
        # Indian Large Cap
        "RELIANCE.NS", "TATAELXSI.NS", "INFY.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS",
        # Tech & Growth
        "BAJAJ-AUTO.NS", "M&M.NS", "TATAMOTORS.NS", "BHARTIARTL.NS",
        # ETFs/Indices (for context)
        "SPY", "QQQ", "^NSEI", "^BSESN"
    ]
    seq_len = 60
    input_size = 15
    batch_size = 32
    
    X, y = prepare_data(symbols, seq_len)
    print(f"Dataset prepared. X: {X.shape}, y: {y.shape}")
    
    if len(X) == 0:
         print("No data found. Training aborted.")
         return

    # LSTM Training
    X_torch = torch.FloatTensor(X)
    y_torch = torch.LongTensor(y)
    dataset = TensorDataset(X_torch, y_torch)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = TradingModel(input_size=input_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print("Training LSTM with batches...")
    for epoch in range(10): # Reduced epochs for stability
        epoch_loss = 0
        model.train()
        for batch_X, batch_y in loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        
        print(f"Epoch {epoch+1}/10, Avg Loss: {epoch_loss/len(loader):.4f}")
            
    torch.save(model.state_dict(), "model.pt")
    print("LSTM saved.")
    
    # XGBoost Training
    print("Training XGBoost...")
    X_flat = X[:, -1, :] 
    xgb_model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)
    xgb_model.fit(X_flat, y)
    
    joblib.dump(xgb_model, "xgb_model.joblib")
    print("XGBoost saved.")

if __name__ == "__main__":
    train()
