"""Volatility & Risk Analysis — Beta, Sharpe, drawdown, correlations."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_fetcher import ASX_STOCKS, PERIOD_MAP, fetch_stock_data, fetch_multiple_stocks, get_stock_name
from src.risk_metrics import (
    calculate_rolling_volatility, calculate_beta, calculate_sharpe_ratio,
    calculate_max_drawdown, calculate_correlation_matrix, calculate_daily_returns,
)

st.set_page_config(page_title="Volatility & Risk", page_icon="⚡", layout="wide")
st.title("Volatility & Risk Analysis")

# Sidebar
st.sidebar.header("Settings")
selected = st.sidebar.multiselect(
    "Select Stocks",
    list(ASX_STOCKS.keys()),
    default=["BHP.AX", "CBA.AX", "CSL.AX", "NAB.AX", "FMG.AX"],
    format_func=lambda x: f"{x} — {ASX_STOCKS[x]}",
)
period = st.sidebar.selectbox("Time Period", list(PERIOD_MAP.keys()), index=3)

if not selected:
    st.warning("Select at least one stock.")
    st.stop()

# Fetch data
stock_data = fetch_multiple_stocks(selected, PERIOD_MAP[period])
benchmark = fetch_stock_data("^AXJO", PERIOD_MAP[period])  # ASX 200 index

# 1. Risk Metrics Table
st.subheader("Risk Metrics Summary")
metrics_rows = []
for ticker, df in stock_data.items():
    beta = calculate_beta(df, benchmark) if not benchmark.empty else float("nan")
    metrics_rows.append({
        "Stock": f"{get_stock_name(ticker)} ({ticker})",
        "Sharpe Ratio": round(calculate_sharpe_ratio(df), 2),
        "Beta vs ASX200": round(beta, 2),
        "Max Drawdown": f"{calculate_max_drawdown(df):.1%}",
        "Ann. Volatility": f"{calculate_daily_returns(df).std() * (252**0.5):.1%}",
    })

st.dataframe(pd.DataFrame(metrics_rows), use_container_width=True, hide_index=True)

# 2. Rolling Volatility
st.subheader("30-Day Rolling Volatility (Annualized)")
fig_vol = go.Figure()
for ticker, df in stock_data.items():
    vol = calculate_rolling_volatility(df, window=30)
    fig_vol.add_trace(go.Scatter(
        x=vol.index, y=vol.values, name=get_stock_name(ticker),
        mode="lines",
    ))

fig_vol.update_layout(
    yaxis_title="Annualized Volatility",
    template="plotly_dark",
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig_vol, use_container_width=True)

# 3. Drawdown Chart
st.subheader("Drawdown Analysis")
fig_dd = go.Figure()
for ticker, df in stock_data.items():
    returns = calculate_daily_returns(df)
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max

    fig_dd.add_trace(go.Scatter(
        x=drawdown.index, y=drawdown.values, name=get_stock_name(ticker),
        fill="tozeroy", mode="lines",
    ))

fig_dd.update_layout(
    yaxis_title="Drawdown",
    yaxis_tickformat=".0%",
    template="plotly_dark",
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig_dd, use_container_width=True)

# 4. Correlation Heatmap
if len(stock_data) >= 2:
    st.subheader("Return Correlation Matrix")
    corr = calculate_correlation_matrix(stock_data)
    corr.index = [get_stock_name(t) for t in corr.index]
    corr.columns = [get_stock_name(t) for t in corr.columns]

    fig_corr = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title="Daily Return Correlations",
    )
    fig_corr.update_layout(template="plotly_dark", height=500)
    st.plotly_chart(fig_corr, use_container_width=True)
