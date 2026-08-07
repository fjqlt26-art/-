import numpy as np
import pandas as pd
import yfinance as yf

from src.config import MA_PERIODS, RSI_PERIOD


def calc_rsi(close: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def get_ticker_snapshot(ticker: str) -> dict:
    """티커의 최신 종가, RSI, 이평선 위치/이격도(%)를 반환"""
    hist = yf.download(
        ticker, period="18mo", interval="1d", progress=False, auto_adjust=False
    )
    if hist.empty:
        raise ValueError(f"{ticker}: 데이터를 가져오지 못했습니다")

    close = hist["Close"].dropna()
    if isinstance(close, pd.DataFrame):  # yfinance 버전에 따라 컬럼이 MultiIndex일 수 있음
        close = close.iloc[:, 0]

    rsi_series = calc_rsi(close)
    latest_close = float(close.iloc[-1])
    latest_rsi = float(rsi_series.iloc[-1])

    ma_info = {}  # period -> {"value": float|None, "position": "위"/"아래"/"데이터부족", "gap_pct": float|None}
    for period in MA_PERIODS:
        ma_series = close.rolling(window=period).mean()
        ma_val = ma_series.iloc[-1]
        if pd.isna(ma_val):
            ma_info[period] = {"value": None, "position": "데이터부족", "gap_pct": None}
            continue
        ma_val = float(ma_val)
        gap_pct = (latest_close - ma_val) / ma_val * 100
        ma_info[period] = {
            "value": ma_val,
            "position": "위" if latest_close >= ma_val else "아래",
            "gap_pct": gap_pct,
        }

    return {
        "ticker": ticker,
        "close": latest_close,
        "rsi": latest_rsi,
        "ma_info": ma_info,
        "date": str(close.index[-1].date()),
    }
