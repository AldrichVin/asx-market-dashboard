"""Risk and volatility metrics for stock analysis."""
import pandas as pd
import numpy as np


def calculate_daily_returns(df: pd.DataFrame) -> pd.Series:
    return df["Close"].pct_change().dropna()


def calculate_rolling_volatility(
    df: pd.DataFrame, window: int = 30,
) -> pd.Series:
    returns = calculate_daily_returns(df)
    return returns.rolling(window=window).std() * np.sqrt(252)  # Annualized


def calculate_beta(
    stock_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
) -> float:
    stock_returns = calculate_daily_returns(stock_df)
    bench_returns = calculate_daily_returns(benchmark_df)

    aligned = pd.DataFrame({
        "stock": stock_returns,
        "bench": bench_returns,
    }).dropna()

    if len(aligned) < 30:
        return float("nan")

    covariance = aligned["stock"].cov(aligned["bench"])
    bench_variance = aligned["bench"].var()
    return covariance / bench_variance if bench_variance != 0 else float("nan")


def calculate_sharpe_ratio(
    df: pd.DataFrame,
    risk_free_rate: float = 0.04,
) -> float:
    returns = calculate_daily_returns(df)
    annual_return = returns.mean() * 252
    annual_vol = returns.std() * np.sqrt(252)
    if annual_vol == 0:
        return float("nan")
    return (annual_return - risk_free_rate) / annual_vol


def calculate_max_drawdown(df: pd.DataFrame) -> float:
    cumulative = (1 + calculate_daily_returns(df)).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def calculate_correlation_matrix(
    stock_data: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    returns_dict = {}
    for ticker, df in stock_data.items():
        returns_dict[ticker] = calculate_daily_returns(df)

    returns_df = pd.DataFrame(returns_dict).dropna()
    return returns_df.corr()
