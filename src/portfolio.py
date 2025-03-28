"""Portfolio simulation and backtesting."""
import pandas as pd
import numpy as np
from .risk_metrics import calculate_daily_returns


def backtest_portfolio(
    stock_data: dict[str, pd.DataFrame],
    weights: dict[str, float],
    initial_investment: float = 10000,
) -> pd.DataFrame:
    returns_dict = {}
    for ticker, df in stock_data.items():
        if ticker in weights:
            returns_dict[ticker] = calculate_daily_returns(df)

    returns_df = pd.DataFrame(returns_dict).dropna()
    if returns_df.empty:
        return pd.DataFrame()

    weight_series = pd.Series(weights)
    weight_series = weight_series[weight_series.index.isin(returns_df.columns)]
    weight_series = weight_series / weight_series.sum()  # Normalize

    portfolio_returns = (returns_df * weight_series).sum(axis=1)
    portfolio_value = initial_investment * (1 + portfolio_returns).cumprod()

    result = pd.DataFrame({
        "Portfolio Value": portfolio_value,
        "Daily Return": portfolio_returns,
        "Cumulative Return": (1 + portfolio_returns).cumprod() - 1,
    })
    return result


def calculate_portfolio_metrics(
    portfolio_df: pd.DataFrame,
    risk_free_rate: float = 0.04,
) -> dict:
    if portfolio_df.empty:
        return {}

    returns = portfolio_df["Daily Return"]
    total_return = portfolio_df["Cumulative Return"].iloc[-1]
    annual_return = returns.mean() * 252
    annual_vol = returns.std() * np.sqrt(252)
    sharpe = (annual_return - risk_free_rate) / annual_vol if annual_vol > 0 else 0

    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    max_dd = ((cumulative - running_max) / running_max).min()

    return {
        "Total Return": f"{total_return:.2%}",
        "Annual Return": f"{annual_return:.2%}",
        "Annual Volatility": f"{annual_vol:.2%}",
        "Sharpe Ratio": f"{sharpe:.2f}",
        "Max Drawdown": f"{max_dd:.2%}",
        "Final Value": f"${portfolio_df['Portfolio Value'].iloc[-1]:,.2f}",
    }
