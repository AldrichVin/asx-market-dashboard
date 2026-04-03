"""Portfolio — Backtest custom allocations against the ASX 200."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data_fetcher import ASX_STOCKS, PERIOD_MAP, fetch_stock_data, fetch_multiple_stocks, get_stock_name
from src.portfolio import backtest_portfolio, calculate_portfolio_metrics
from src.risk_metrics import calculate_daily_returns
from src.ui import load_css, apply_chart_style, show_chart, page_header, NAVY, NAVY_LIGHT, GRAY, GREEN, RED

st.set_page_config(page_title="Portfolio", layout="wide")
load_css()
page_header("Portfolio", "Backtest custom allocations vs the ASX 200 benchmark.")

st.sidebar.markdown("#### Controls")
selected = st.sidebar.multiselect(
    "Stocks",
    list(ASX_STOCKS.keys()),
    default=["BHP.AX", "CBA.AX", "CSL.AX", "WES.AX"],
    format_func=lambda x: f"{x.replace('.AX', '')} — {ASX_STOCKS[x]}",
)
period = st.sidebar.selectbox("Period", list(PERIOD_MAP.keys()), index=3)
initial = st.sidebar.number_input("Initial Investment (AUD)", value=10000, step=1000, min_value=1000)

if not selected:
    st.info("Select at least one stock.")
    st.stop()

# Weight sliders
st.sidebar.markdown("#### Allocation")
weights = {}
for ticker in selected:
    name = get_stock_name(ticker)
    weights[ticker] = st.sidebar.slider(f"{name}", 0, 100, 100 // len(selected), key=ticker)

total_weight = sum(weights.values())
if total_weight == 0:
    st.warning("Total allocation is zero. Adjust the sliders.")
    st.stop()

stock_data = fetch_multiple_stocks(selected, PERIOD_MAP[period])
benchmark = fetch_stock_data("^AXJO", PERIOD_MAP[period])

portfolio_df = backtest_portfolio(stock_data, weights, initial)
if portfolio_df.empty:
    st.error("Unable to compute portfolio.")
    st.stop()

# Portfolio metrics
metrics = calculate_portfolio_metrics(portfolio_df)
st.subheader("Performance Summary")
cols = st.columns(len(metrics))
for col, (label, value) in zip(cols, metrics.items()):
    col.metric(label, value)

# Portfolio value chart
st.subheader("Portfolio Value")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=portfolio_df.index, y=portfolio_df["Portfolio Value"],
    name="Portfolio", line=dict(color=NAVY, width=2),
    fill="tozeroy", fillcolor="rgba(30,58,95,0.04)",
))

if not benchmark.empty:
    bench_ret = calculate_daily_returns(benchmark)
    bench_value = initial * (1 + bench_ret).cumprod()
    fig.add_trace(go.Scatter(
        x=bench_value.index, y=bench_value.values,
        name="ASX 200", line=dict(color=GRAY, width=1.5, dash="dash"),
    ))

apply_chart_style(fig, 420)
fig.update_yaxes(title_text="AUD", tickprefix="$")
show_chart(fig)

# Cumulative returns comparison
st.subheader("Cumulative Returns")
fig_cum = go.Figure()
fig_cum.add_trace(go.Scatter(
    x=portfolio_df.index, y=portfolio_df["Cumulative Return"],
    name="Portfolio", line=dict(color=NAVY, width=2),
))
if not benchmark.empty:
    bench_cum = (1 + bench_ret).cumprod() - 1
    fig_cum.add_trace(go.Scatter(
        x=bench_cum.index, y=bench_cum.values,
        name="ASX 200", line=dict(color=GRAY, width=1.5, dash="dash"),
    ))

apply_chart_style(fig_cum, 350)
fig_cum.update_yaxes(tickformat=".0%")
show_chart(fig_cum)

# Allocation display
st.subheader("Allocation")
alloc_df = pd.DataFrame([
    {"Stock": get_stock_name(t), "Ticker": t.replace(".AX", ""), "Weight": f"{w/total_weight:.1%}"}
    for t, w in weights.items()
])
st.dataframe(alloc_df, use_container_width=True, hide_index=True)
