"""Technical analysis indicators for stock data."""
import pandas as pd
import numpy as np


def add_moving_averages(
    df: pd.DataFrame,
    windows: list[int] = [20, 50, 200],
) -> pd.DataFrame:
    df = df.copy()
    for w in windows:
        if len(df) >= w:
            df[f"SMA_{w}"] = df["Close"].rolling(window=w).mean()
    return df


def add_bollinger_bands(
    df: pd.DataFrame, window: int = 20, num_std: float = 2.0,
) -> pd.DataFrame:
    df = df.copy()
    sma = df["Close"].rolling(window=window).mean()
    std = df["Close"].rolling(window=window).std()
    df["BB_Upper"] = sma + (num_std * std)
    df["BB_Lower"] = sma - (num_std * std)
    df["BB_Middle"] = sma
    return df


def calculate_rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def detect_ma_crossovers(df: pd.DataFrame) -> pd.DataFrame:
    df = add_moving_averages(df, [50, 200])
    if "SMA_50" not in df.columns or "SMA_200" not in df.columns:
        return pd.DataFrame()

    df = df.dropna(subset=["SMA_50", "SMA_200"])
    df["Signal"] = np.where(df["SMA_50"] > df["SMA_200"], 1, -1)
    df["Crossover"] = df["Signal"].diff()

    signals = df[df["Crossover"] != 0].copy()
    signals["Type"] = np.where(signals["Crossover"] > 0, "Golden Cross", "Death Cross")
    return signals[["Close", "SMA_50", "SMA_200", "Type"]]
