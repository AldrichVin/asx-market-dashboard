"""Sector Performance — ASX sector comparison."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_fetcher import ASX_SECTORS, PERIOD_MAP, fetch_multiple_stocks, get_stock_name
from src.risk_metrics import calculate_daily_returns
from src.ui import load_css, apply_chart_style, show_chart, page_header, NAVY, NAVY_LIGHT, CHART_COLORS, GREEN, RED

st.set_page_config(page_title="Sectors", layout="wide")
load_css()
page_header("Sectors", "Sector-level performance across the ASX.")

period = st.sidebar.selectbox("Period", list(PERIOD_MAP.keys()), index=3)

all_tickers = [t for tickers in ASX_SECTORS.values() for t in tickers]
stock_data = fetch_multiple_stocks(all_tickers, PERIOD_MAP[period])

if not stock_data:
    st.error("Unable to fetch data.")
    st.stop()

# Sector returns
sector_returns = {}
for sector, tickers in ASX_SECTORS.items():
    rets = []
    for t in tickers:
        if t in stock_data:
            df = stock_data[t]
            rets.append((df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1)
    if rets:
        sector_returns[sector] = np.mean(rets)

st.subheader(f"Sector Returns — {period}")
sector_df = pd.DataFrame({
    "Sector": list(sector_returns.keys()),
    "Return": list(sector_returns.values()),
}).sort_values("Return", ascending=True)

colors = [GREEN if r >= 0 else RED for r in sector_df["Return"]]
fig = go.Figure(go.Bar(
    x=sector_df["Return"], y=sector_df["Sector"],
    orientation="h", marker_color=colors,
    text=[f"{r:+.1%}" for r in sector_df["Return"]],
    textposition="auto", textfont=dict(size=11),
))
apply_chart_style(fig, 380)
fig.update_xaxes(tickformat=".0%")
show_chart(fig)

# Cumulative
st.subheader("Cumulative Returns")
fig_cum = go.Figure()
for i, (sector, tickers) in enumerate(ASX_SECTORS.items()):
    sector_cum = None
    n = 0
    for t in tickers:
        if t in stock_data:
            cum = (1 + calculate_daily_returns(stock_data[t])).cumprod() - 1
            if sector_cum is None:
                sector_cum = cum.copy()
            else:
                aligned = pd.DataFrame({"a": sector_cum, "b": cum}).dropna()
                sector_cum = aligned.mean(axis=1)
            n += 1
    if sector_cum is not None:
        fig_cum.add_trace(go.Scatter(
            x=sector_cum.index, y=sector_cum.values, name=sector,
            line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=1.5),
        ))

apply_chart_style(fig_cum, 420)
fig_cum.update_yaxes(tickformat=".0%")
show_chart(fig_cum)

# Stock breakdown
st.subheader("Breakdown by Sector")
for sector, tickers in ASX_SECTORS.items():
    stocks = []
    for t in tickers:
        if t in stock_data:
            df = stock_data[t]
            ret = (df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1
            stocks.append({
                "Stock": get_stock_name(t),
                "Ticker": t.replace(".AX", ""),
                "Return": ret,
                "Price": f"${df['Close'].iloc[-1]:.2f}",
            })
    if stocks:
        st.markdown(f"**{sector}**")
        st.dataframe(
            pd.DataFrame(stocks).style.format({"Return": "{:+.2%}"}),
            use_container_width=True, hide_index=True,
        )
