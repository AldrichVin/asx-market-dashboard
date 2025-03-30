"""Sector Performance — ASX sector comparison and relative strength."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_fetcher import ASX_SECTORS, PERIOD_MAP, fetch_multiple_stocks, get_stock_name
from src.risk_metrics import calculate_daily_returns

st.set_page_config(page_title="Sector Performance", page_icon="🏭", layout="wide")
st.title("ASX Sector Performance")

# Sidebar
period = st.sidebar.selectbox("Time Period", list(PERIOD_MAP.keys()), index=3)

# Fetch all sector stocks
all_tickers = [t for tickers in ASX_SECTORS.values() for t in tickers]
stock_data = fetch_multiple_stocks(all_tickers, PERIOD_MAP[period])

if not stock_data:
    st.error("Unable to fetch stock data. Please try again.")
    st.stop()

# Calculate sector returns
sector_returns = {}
for sector, tickers in ASX_SECTORS.items():
    sector_rets = []
    for ticker in tickers:
        if ticker in stock_data:
            df = stock_data[ticker]
            total_return = (df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1
            sector_rets.append(total_return)
    if sector_rets:
        sector_returns[sector] = np.mean(sector_rets)

# 1. Sector Return Comparison
st.subheader(f"Sector Returns — {period}")
sector_df = pd.DataFrame({
    "Sector": list(sector_returns.keys()),
    "Return": list(sector_returns.values()),
}).sort_values("Return", ascending=True)

colors = ["#2ecc71" if r >= 0 else "#e74c3c" for r in sector_df["Return"]]
fig = go.Figure(go.Bar(
    x=sector_df["Return"],
    y=sector_df["Sector"],
    orientation="h",
    marker_color=colors,
    text=[f"{r:.1%}" for r in sector_df["Return"]],
    textposition="auto",
))
fig.update_layout(
    xaxis_title="Total Return",
    xaxis_tickformat=".0%",
    template="plotly_dark",
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

# 2. Cumulative Returns by Sector
st.subheader("Cumulative Sector Returns Over Time")
fig_cum = go.Figure()

for sector, tickers in ASX_SECTORS.items():
    sector_cum = None
    count = 0
    for ticker in tickers:
        if ticker in stock_data:
            returns = calculate_daily_returns(stock_data[ticker])
            cum = (1 + returns).cumprod() - 1
            if sector_cum is None:
                sector_cum = cum.copy()
            else:
                aligned = pd.DataFrame({"a": sector_cum, "b": cum}).dropna()
                sector_cum = aligned.mean(axis=1)
            count += 1

    if sector_cum is not None and count > 0:
        fig_cum.add_trace(go.Scatter(
            x=sector_cum.index, y=sector_cum.values,
            name=sector, mode="lines",
        ))

fig_cum.update_layout(
    yaxis_title="Cumulative Return",
    yaxis_tickformat=".0%",
    template="plotly_dark",
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
st.plotly_chart(fig_cum, use_container_width=True)

# 3. Individual Stock Returns within Sectors
st.subheader("Individual Stock Returns by Sector")

for sector, tickers in ASX_SECTORS.items():
    stocks_in_sector = []
    for ticker in tickers:
        if ticker in stock_data:
            df = stock_data[ticker]
            ret = (df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1
            stocks_in_sector.append({
                "Stock": get_stock_name(ticker),
                "Ticker": ticker,
                "Return": ret,
                "Latest Price": f"${df['Close'].iloc[-1]:.2f}",
            })

    if stocks_in_sector:
        st.markdown(f"**{sector}**")
        st.dataframe(
            pd.DataFrame(stocks_in_sector).style.format({"Return": "{:.2%}"}),
            use_container_width=True, hide_index=True,
        )
