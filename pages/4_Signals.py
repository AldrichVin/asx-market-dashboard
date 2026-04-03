"""Signals — MA crossovers, RSI, and trend projections."""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_fetcher import ASX_STOCKS, PERIOD_MAP, fetch_stock_data, get_stock_name
from src.technical_indicators import calculate_rsi, detect_ma_crossovers, add_bollinger_bands
from src.ui import load_css, apply_chart_style, show_chart, page_header, NAVY, NAVY_LIGHT, GRAY, GREEN, RED, GRID

st.set_page_config(page_title="Signals", layout="wide")
load_css()
page_header("Signals", "Trend detection and technical projections.")

st.sidebar.markdown("#### Controls")
ticker = st.sidebar.selectbox(
    "Stock",
    list(ASX_STOCKS.keys()),
    format_func=lambda x: f"{x.replace('.AX', '')} — {ASX_STOCKS[x]}",
)
period = st.sidebar.selectbox("Period", list(PERIOD_MAP.keys()), index=3)

df = fetch_stock_data(ticker, PERIOD_MAP[period])
if df.empty:
    st.error("Unable to fetch data.")
    st.stop()

name = get_stock_name(ticker)

# Price with Bollinger Bands
st.subheader(f"{name} — Price & Bollinger Bands")
bb = add_bollinger_bands(df)
fig_bb = go.Figure()
fig_bb.add_trace(go.Scatter(
    x=bb.index, y=bb["BB_Upper"], name="Upper Band",
    line=dict(color=GRAY, width=1, dash="dot"), showlegend=False,
))
fig_bb.add_trace(go.Scatter(
    x=bb.index, y=bb["BB_Lower"], name="Lower Band",
    line=dict(color=GRAY, width=1, dash="dot"), fill="tonexty",
    fillcolor="rgba(30,58,95,0.04)", showlegend=False,
))
fig_bb.add_trace(go.Scatter(
    x=bb.index, y=bb["Close"], name="Close",
    line=dict(color=NAVY, width=2),
))
fig_bb.add_trace(go.Scatter(
    x=bb.index, y=bb["BB_Middle"], name="SMA 20",
    line=dict(color=NAVY_LIGHT, width=1, dash="dash"),
))
apply_chart_style(fig_bb, 400)
fig_bb.update_yaxes(title_text="AUD")
show_chart(fig_bb)

# RSI
st.subheader("Relative Strength Index (14)")
rsi = calculate_rsi(df)
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(
    x=rsi.index, y=rsi.values, name="RSI",
    line=dict(color=NAVY, width=1.5),
))
fig_rsi.add_hline(y=70, line_dash="dot", line_color=RED, line_width=1, annotation_text="Overbought")
fig_rsi.add_hline(y=30, line_dash="dot", line_color=GREEN, line_width=1, annotation_text="Oversold")
fig_rsi.add_hrect(y0=30, y1=70, fillcolor=GRID, opacity=0.3, line_width=0)
apply_chart_style(fig_rsi, 280)
fig_rsi.update_yaxes(range=[0, 100], title_text="RSI")
show_chart(fig_rsi)

# MA Crossovers
st.subheader("Moving Average Crossovers (50/200)")
signals = detect_ma_crossovers(df)
if signals.empty:
    st.caption("Not enough data for 50/200 MA crossover detection.")
else:
    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(
        x=df.index, y=df["Close"], name="Close",
        line=dict(color=NAVY, width=1.5),
    ))

    golden = signals[signals["Type"] == "Golden Cross"]
    death = signals[signals["Type"] == "Death Cross"]

    if not golden.empty:
        fig_ma.add_trace(go.Scatter(
            x=golden.index, y=golden["Close"], mode="markers",
            name="Golden Cross", marker=dict(color=GREEN, size=10, symbol="circle"),
        ))
    if not death.empty:
        fig_ma.add_trace(go.Scatter(
            x=death.index, y=death["Close"], mode="markers",
            name="Death Cross", marker=dict(color=RED, size=10, symbol="circle"),
        ))

    fig_ma.add_trace(go.Scatter(
        x=signals.index[:1], y=signals["SMA_50"][:0],  # dummy for SMA traces
        visible=True, showlegend=False,
    ))

    apply_chart_style(fig_ma, 380)
    fig_ma.update_yaxes(title_text="AUD")
    show_chart(fig_ma)

    if not signals.empty:
        st.dataframe(
            signals[["Type", "Close"]].reset_index().rename(
                columns={"index": "Date", "Close": "Price"}
            ).style.format({"Price": "${:.2f}"}),
            use_container_width=True, hide_index=True,
        )

# Linear regression projection
st.subheader("30-Day Trend Projection")
close = df["Close"].dropna()
x = np.arange(len(close))
coeffs = np.polyfit(x, close.values, 1)
slope, intercept = coeffs

projection_days = 30
x_proj = np.arange(len(close), len(close) + projection_days)
y_proj = slope * x_proj + intercept

last_date = close.index[-1]
proj_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=projection_days)

trend_line = slope * x + intercept

fig_proj = go.Figure()
fig_proj.add_trace(go.Scatter(
    x=close.index, y=close.values, name="Actual",
    line=dict(color=NAVY, width=2),
))
fig_proj.add_trace(go.Scatter(
    x=close.index, y=trend_line, name="Trend",
    line=dict(color=GRAY, width=1, dash="dash"),
))

residual_std = np.std(close.values - trend_line)
upper = y_proj + 1.96 * residual_std
lower = y_proj - 1.96 * residual_std

fig_proj.add_trace(go.Scatter(
    x=proj_dates, y=upper, mode="lines",
    line=dict(width=0), showlegend=False,
))
fig_proj.add_trace(go.Scatter(
    x=proj_dates, y=lower, mode="lines", name="95% Interval",
    line=dict(width=0), fill="tonexty",
    fillcolor="rgba(30,58,95,0.08)",
))
fig_proj.add_trace(go.Scatter(
    x=proj_dates, y=y_proj, name="Projection",
    line=dict(color=NAVY_LIGHT, width=2, dash="dot"),
))

apply_chart_style(fig_proj, 400)
fig_proj.update_yaxes(title_text="AUD")
show_chart(fig_proj)

daily_change = slope
st.caption(
    f"Linear trend: {'+'if daily_change >= 0 else ''}{daily_change:.3f} AUD/day  |  "
    f"Projected 30-day price: ${y_proj[-1]:.2f}"
)
