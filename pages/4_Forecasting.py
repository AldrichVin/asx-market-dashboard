"""Forecasting — MA crossover signals and linear regression trend projection."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_fetcher import ASX_STOCKS, fetch_stock_data, get_stock_name
from src.technical_indicators import detect_ma_crossovers, add_moving_averages, calculate_rsi

st.set_page_config(page_title="Forecasting", page_icon="🔮", layout="wide")
st.title("Forecasting & Technical Signals")

st.warning(
    "**Disclaimer**: This analysis is for educational purposes only. "
    "It does not constitute financial advice. Past performance does not "
    "guarantee future results."
)

# Sidebar
ticker = st.sidebar.selectbox(
    "Select Stock",
    list(ASX_STOCKS.keys()),
    format_func=lambda x: f"{x} — {ASX_STOCKS[x]}",
)
forecast_days = st.sidebar.slider("Forecast Horizon (days)", 30, 180, 90)

# Fetch 2 years of data for MA crossovers
df = fetch_stock_data(ticker, "2y")

if df.empty:
    st.error(f"No data available for {ticker}")
    st.stop()

name = get_stock_name(ticker)

# 1. Moving Average Crossover Signals
st.subheader(f"Moving Average Crossover — {name}")

df_ma = add_moving_averages(df, [50, 200])
signals = detect_ma_crossovers(df)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma["Close"], name="Close", line=dict(color="#1f77b4", width=1.5)))

if "SMA_50" in df_ma.columns:
    fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma["SMA_50"], name="SMA 50", line=dict(color="#ff7f0e", dash="dash")))
if "SMA_200" in df_ma.columns:
    fig.add_trace(go.Scatter(x=df_ma.index, y=df_ma["SMA_200"], name="SMA 200", line=dict(color="#d62728", dash="dash")))

# Mark crossover points
if not signals.empty:
    golden = signals[signals["Type"] == "Golden Cross"]
    death = signals[signals["Type"] == "Death Cross"]

    if not golden.empty:
        fig.add_trace(go.Scatter(
            x=golden.index, y=golden["Close"], mode="markers",
            name="Golden Cross (Buy)", marker=dict(color="#2ecc71", size=12, symbol="triangle-up"),
        ))
    if not death.empty:
        fig.add_trace(go.Scatter(
            x=death.index, y=death["Close"], mode="markers",
            name="Death Cross (Sell)", marker=dict(color="#e74c3c", size=12, symbol="triangle-down"),
        ))

fig.update_layout(template="plotly_dark", height=500, yaxis_title="Price (AUD)")
st.plotly_chart(fig, use_container_width=True)

if not signals.empty:
    st.markdown("**Recent Signals:**")
    recent = signals.tail(5).copy()
    recent.index = recent.index.strftime("%Y-%m-%d")
    st.dataframe(recent[["Close", "Type"]], use_container_width=True)
else:
    st.info("No MA crossover signals detected in this period.")

# 2. RSI (Relative Strength Index)
st.subheader("RSI (14-day)")
rsi = calculate_rsi(df)

fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=rsi.index, y=rsi.values, name="RSI", line=dict(color="#9b59b6")))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="#e74c3c", annotation_text="Overbought (70)")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="#2ecc71", annotation_text="Oversold (30)")
fig_rsi.update_layout(template="plotly_dark", height=300, yaxis_title="RSI", yaxis_range=[0, 100])
st.plotly_chart(fig_rsi, use_container_width=True)

current_rsi = rsi.iloc[-1]
if current_rsi > 70:
    st.warning(f"RSI = {current_rsi:.1f} — Stock may be **overbought**")
elif current_rsi < 30:
    st.success(f"RSI = {current_rsi:.1f} — Stock may be **oversold**")
else:
    st.info(f"RSI = {current_rsi:.1f} — Neutral zone")

# 3. Linear Regression Trend Projection
st.subheader(f"Linear Trend Projection — {forecast_days} Days")

# Use last 6 months for trend
recent_df = df.tail(126).copy()
recent_df["Day"] = range(len(recent_df))

X = recent_df[["Day"]].values
y = recent_df["Close"].values

model = LinearRegression()
model.fit(X, y)

# Project forward
future_days = np.arange(len(recent_df), len(recent_df) + forecast_days).reshape(-1, 1)
future_prices = model.predict(future_days)
future_dates = pd.date_range(start=recent_df.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq="B")

# Confidence band (using residual std)
residuals = y - model.predict(X)
std_residual = residuals.std()

fig_proj = go.Figure()
fig_proj.add_trace(go.Scatter(
    x=recent_df.index, y=recent_df["Close"],
    name="Historical", line=dict(color="#1f77b4"),
))
fig_proj.add_trace(go.Scatter(
    x=future_dates, y=future_prices,
    name="Projection", line=dict(color="#ff7f0e", dash="dash"),
))
fig_proj.add_trace(go.Scatter(
    x=future_dates, y=future_prices + 2 * std_residual,
    name="Upper Band (2σ)", line=dict(color="#ff7f0e", width=0),
    showlegend=False,
))
fig_proj.add_trace(go.Scatter(
    x=future_dates, y=future_prices - 2 * std_residual,
    name="Lower Band (2σ)", line=dict(color="#ff7f0e", width=0),
    fill="tonexty", fillcolor="rgba(255,127,14,0.1)",
    showlegend=False,
))

fig_proj.update_layout(template="plotly_dark", height=450, yaxis_title="Price (AUD)")
st.plotly_chart(fig_proj, use_container_width=True)

trend_direction = "upward" if model.coef_[0] > 0 else "downward"
daily_change = model.coef_[0]
st.markdown(f"""
**Trend Summary:**
- Direction: **{trend_direction}** (${daily_change:.2f}/day)
- Projected price in {forecast_days} days: **${future_prices[-1]:.2f}**
- Confidence band: ${future_prices[-1] - 2*std_residual:.2f} — ${future_prices[-1] + 2*std_residual:.2f}
""")
