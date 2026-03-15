
import yfinance as yf
import pandas as pd

def moving_average_strategy(symbol):

    df = yf.download(symbol, period="3mo", interval="1d")

    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma50"] = df["Close"].rolling(50).mean()

    if df["ma20"].iloc[-1] > df["ma50"].iloc[-1]:
        return "BUY"
    else:
        return "SELL"
